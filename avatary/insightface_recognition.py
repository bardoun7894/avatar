"""
InsightFace-based Face Recognition System
Uses InsightFace for accurate and fast face recognition
"""

import os
import sqlite3
import pickle
from typing import Optional, List
from pathlib import Path
import numpy as np
from PIL import Image
import io
import logging

from insightface.app import FaceAnalysis
from models import FaceMatch

# Import workflow analyzer
try:
    from workflow_analyzer import workflow_analyzer
    WORKFLOW_TRACKING = True
except ImportError:
    WORKFLOW_TRACKING = False

logger = logging.getLogger(__name__)


class InsightFaceDatabase:
    """SQLite database for storing face embeddings"""

    def __init__(self, db_path: str = "avatary/data/insightface.db"):
        self.db_path = db_path

        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # Initialize database
        self._init_db()

    def _init_db(self):
        """Create faces table if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS faces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT NOT NULL,
                phone TEXT NOT NULL UNIQUE,
                email TEXT,
                embedding BLOB NOT NULL,
                image BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()
        logger.info(f"✅ InsightFace database initialized: {self.db_path}")

    def save_face(
        self,
        user_name: str,
        phone: str,
        embedding: np.ndarray,
        image_bytes: Optional[bytes] = None,
        email: Optional[str] = None
    ) -> bool:
        """Save face embedding to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Serialize embedding
            embedding_blob = pickle.dumps(embedding)

            # Insert or replace
            cursor.execute("""
                INSERT OR REPLACE INTO faces
                (user_name, phone, email, embedding, image, created_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (user_name, phone, email, embedding_blob, image_bytes))

            conn.commit()
            conn.close()

            logger.info(f"✅ Saved face for {user_name} ({phone})")
            return True

        except Exception as e:
            logger.error(f"Failed to save face: {e}")
            return False

    def get_all_faces(self) -> List[dict]:
        """Get all registered faces"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT user_name, phone, email, embedding, last_seen
            FROM faces
        """)

        faces = []
        for row in cursor.fetchall():
            faces.append({
                "user_name": row[0],
                "phone": row[1],
                "email": row[2],
                "embedding": pickle.loads(row[3]),
                "last_seen": row[4]
            })

        conn.close()
        return faces

    def update_last_seen(self, phone: str):
        """Update last_seen timestamp"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE faces
            SET last_seen = CURRENT_TIMESTAMP
            WHERE phone = ?
        """, (phone,))

        conn.commit()
        conn.close()

    def delete_person(self, phone: str) -> bool:
        """Delete a person from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("DELETE FROM faces WHERE phone = ?", (phone,))

            conn.commit()
            conn.close()

            logger.info(f"✅ Deleted person: {phone}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete person: {e}")
            return False


class InsightFaceRecognition:
    """Face recognition using InsightFace with lazy loading for memory efficiency"""

    def __init__(self, threshold: float = 0.4):
        """
        Initialize InsightFace recognition

        Args:
            threshold: Cosine similarity threshold (0.0-1.0)
                      Lower = stricter matching
                      Default 0.4 is recommended for good accuracy
        """
        self.threshold = threshold
        self.db = InsightFaceDatabase()
        self.app = None  # Lazy load - only load when first needed
        self._loading = False

    def _ensure_model_loaded(self):
        """Lazy load InsightFace model only when needed"""
        if self.app is None and not self._loading:
            self._loading = True

            if WORKFLOW_TRACKING:
                workflow_analyzer.start_step("InsightFace Model Loading (Lazy)")

            logger.info("🔄 Loading InsightFace model (lazy load)...")
            self.app = FaceAnalysis(
                name='buffalo_l',  # High accuracy model
                providers=['CPUExecutionProvider']  # Use CPU
            )
            self.app.prepare(ctx_id=0, det_size=(640, 640))

            if WORKFLOW_TRACKING:
                workflow_analyzer.complete_step()

            logger.info("✅ InsightFace model loaded!")
            self._loading = False

    def register_person(
        self,
        image_bytes: bytes,
        user_name: str,
        phone: str,
        email: Optional[str] = None
    ) -> bool:
        """
        Register a new person

        Args:
            image_bytes: Image bytes (JPEG/PNG)
            user_name: Person's name
            phone: Phone number (unique identifier)
            email: Email address (optional)

        Returns:
            True if registered successfully
        """
        try:
            # Ensure model is loaded (lazy loading)
            self._ensure_model_loaded()

            # Convert bytes to PIL Image
            img = Image.open(io.BytesIO(image_bytes))
            img_array = np.array(img.convert('RGB'))

            # Detect faces
            faces = self.app.get(img_array)

            if len(faces) == 0:
                logger.error("❌ No face detected in image")
                return False

            if len(faces) > 1:
                logger.warning("⚠️  Multiple faces detected, using first face")

            # Get embedding (512-dimensional)
            face = faces[0]
            embedding = face.embedding

            # Save to database
            success = self.db.save_face(
                user_name=user_name,
                phone=phone,
                embedding=embedding,
                image_bytes=image_bytes,
                email=email
            )

            if success:
                logger.info(f"✅ Registered {user_name} ({phone})")

            return success

        except Exception as e:
            logger.error(f"Registration failed: {e}")
            return False

    def recognize_person(self, image_bytes: bytes) -> FaceMatch:
        """
        Recognize a person from image

        Args:
            image_bytes: Image bytes (JPEG/PNG)

        Returns:
            FaceMatch object with recognition results
        """
        try:
            # Ensure model is loaded (lazy loading)
            self._ensure_model_loaded()

            # Convert bytes to PIL Image
            img = Image.open(io.BytesIO(image_bytes))
            img_array = np.array(img.convert('RGB'))

            # Detect faces
            faces = self.app.get(img_array)

            if len(faces) == 0:
                logger.info("👤 No face detected")
                return FaceMatch(matched=False)

            # Get embedding
            face = faces[0]
            current_embedding = face.embedding

            # Load all registered faces
            registered_faces = self.db.get_all_faces()

            if len(registered_faces) == 0:
                logger.info("👤 No registered faces in database")
                return FaceMatch(matched=False)

            # Find best match using cosine similarity
            best_match = None
            best_similarity = -1.0

            for registered in registered_faces:
                # Calculate cosine similarity
                similarity = self._cosine_similarity(
                    current_embedding,
                    registered["embedding"]
                )

                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = registered

            # Check if similarity meets threshold
            # InsightFace uses cosine similarity: higher is better
            # Convert to distance for threshold comparison
            distance = 1.0 - best_similarity

            if distance <= self.threshold and best_match:
                # Update last_seen
                self.db.update_last_seen(best_match["phone"])

                logger.info(
                    f"✅ RECOGNIZED: {best_match['user_name']} "
                    f"(similarity: {best_similarity:.3f}, distance: {distance:.3f})"
                )

                return FaceMatch(
                    matched=True,
                    user_name=best_match["user_name"],
                    phone=best_match["phone"],
                    email=best_match.get("email"),
                    confidence=float(best_similarity)
                )
            else:
                logger.info(
                    f"❌ No match found (best distance: {distance:.3f}, "
                    f"threshold: {self.threshold})"
                )
                return FaceMatch(matched=False)

        except Exception as e:
            logger.error(f"Recognition failed: {e}")
            return FaceMatch(matched=False)

    @staticmethod
    def _cosine_similarity(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate cosine similarity between two embeddings"""
        # Normalize embeddings
        embedding1_norm = embedding1 / np.linalg.norm(embedding1)
        embedding2_norm = embedding2 / np.linalg.norm(embedding2)

        # Calculate cosine similarity
        similarity = np.dot(embedding1_norm, embedding2_norm)

        return float(similarity)

    def get_registered_people(self) -> List[dict]:
        """Get list of all registered people"""
        faces = self.db.get_all_faces()

        return [
            {
                "name": face["user_name"],
                "phone": face["phone"],
                "email": face.get("email"),
                "last_seen": face["last_seen"]
            }
            for face in faces
        ]

    def delete_person(self, phone: str) -> bool:
        """Delete a person from the system"""
        return self.db.delete_person(phone)


# Global instance
face_recognizer = InsightFaceRecognition(threshold=0.4)
