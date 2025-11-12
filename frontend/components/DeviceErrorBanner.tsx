import { useEffect, useState } from 'react'

interface DeviceErrorBannerProps {
  error: string | null
  onRetry: () => void
  onDismiss: () => void
}

export default function DeviceErrorBanner({ error, onRetry, onDismiss }: DeviceErrorBannerProps) {
  const [show, setShow] = useState(false)

  useEffect(() => {
    setShow(!!error)
  }, [error])

  if (!show || !error) return null

  const getErrorDetails = (errorMsg: string) => {
    if (errorMsg.includes('NotReadableError') || errorMsg.includes('Device in use')) {
      return {
        title: 'الكاميرا أو الميكروفون قيد الاستخدام',
        titleEn: 'Camera/Microphone In Use',
        message: 'جهازك قيد الاستخدام من قبل تطبيق آخر',
        messageEn: 'Your device is being used by another application',
        solutions: [
          'أغلق أي تطبيقات أخرى تستخدم الكاميرا/الميكروفون',
          'Close other tabs or apps using camera/microphone',
          'تحقق من إعدادات الخصوصية في المتصفح',
          'Check browser privacy settings'
        ],
        icon: '📹',
        color: 'from-orange-500/20 to-red-500/20'
      }
    } else if (errorMsg.includes('NotAllowedError') || errorMsg.includes('Permission denied')) {
      return {
        title: 'تم رفض الإذن',
        titleEn: 'Permission Denied',
        message: 'يجب السماح بالوصول إلى الكاميرا والميكروفون',
        messageEn: 'Camera and microphone access required',
        solutions: [
          'انقر على أيقونة القفل في شريط العنوان',
          'Click the lock icon in the address bar',
          'اسمح بالوصول إلى الكاميرا والميكروفون',
          'Allow camera and microphone access'
        ],
        icon: '🔒',
        color: 'from-yellow-500/20 to-orange-500/20'
      }
    } else if (errorMsg.includes('NotFoundError') || errorMsg.includes('not found')) {
      return {
        title: 'الجهاز غير موجود',
        titleEn: 'Device Not Found',
        message: 'لم يتم العثور على كاميرا أو ميكروفون',
        messageEn: 'No camera or microphone detected',
        solutions: [
          'تحقق من توصيل الأجهزة بشكل صحيح',
          'Check device connections',
          'أعد تشغيل المتصفح',
          'Restart your browser'
        ],
        icon: '🔍',
        color: 'from-blue-500/20 to-purple-500/20'
      }
    } else {
      return {
        title: 'خطأ في الجهاز',
        titleEn: 'Device Error',
        message: 'حدث خطأ أثناء الوصول إلى الأجهزة',
        messageEn: 'An error occurred accessing devices',
        solutions: [
          'أعد تحميل الصفحة',
          'Reload the page',
          'تحقق من اتصال الأجهزة',
          'Check device connections'
        ],
        icon: '⚠️',
        color: 'from-red-500/20 to-pink-500/20'
      }
    }
  }

  const details = getErrorDetails(error)

  const handleDismiss = () => {
    setShow(false)
    setTimeout(() => onDismiss(), 300)
  }

  return (
    <div className="fixed top-4 left-4 right-4 md:left-auto md:right-4 md:w-96 z-50 animate-slide-down">
      {/* Glassmorphism container */}
      <div className="relative backdrop-blur-xl bg-white/10 dark:bg-black/20 rounded-2xl shadow-2xl border border-white/20 dark:border-white/10 p-5 overflow-hidden">
        {/* Gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent pointer-events-none"></div>
        
        {/* Content */}
        <div className="relative">
          {/* Header with icon and close button */}
          <div className="flex items-start gap-4 mb-3">
            <div className={`flex-shrink-0 p-2 rounded-xl bg-gradient-to-br ${details.color} backdrop-blur-sm border border-white/20`}>
              <span className="text-3xl">{details.icon}</span>
            </div>
            
            <div className="flex-1">
              <h3 className="font-bold text-white text-lg drop-shadow-md">{details.title}</h3>
              <p className="text-sm text-white/70 drop-shadow">{details.titleEn}</p>
            </div>
            
            <button
              onClick={handleDismiss}
              className="flex-shrink-0 text-white/60 hover:text-white transition-colors"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          </div>
          
          {/* Message */}
          <div className="mb-4 p-3 rounded-lg bg-white/5 backdrop-blur-sm border border-white/10">
            <p className="text-sm text-white/90 mb-1">{details.message}</p>
            <p className="text-xs text-white/70">{details.messageEn}</p>
          </div>
          
          {/* Solutions */}
          <div className="mb-4 space-y-1">
            <p className="text-xs font-semibold text-white/80 mb-2">الحلول / Solutions:</p>
            {details.solutions.map((solution, idx) => (
              <p key={idx} className="text-xs text-white/70 flex items-start gap-2">
                <span className="text-white/40">•</span>
                <span>{solution}</span>
              </p>
            ))}
          </div>
          
          {/* Actions */}
          <div className="flex gap-2">
            <button
              onClick={onRetry}
              className="flex-1 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white px-4 py-2.5 rounded-xl text-sm font-semibold transition-all duration-300 shadow-lg hover:shadow-xl hover:scale-105"
            >
              إعادة المحاولة / Retry
            </button>
            <button
              onClick={handleDismiss}
              className="px-4 py-2.5 text-white/90 hover:text-white bg-white/10 hover:bg-white/20 backdrop-blur-sm rounded-xl text-sm font-medium transition-all duration-300 border border-white/20 hover:border-white/30"
            >
              إغلاق
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
