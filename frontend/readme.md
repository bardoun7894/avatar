# Galileo Glass UI Design System


## Overview


The Galileo Glass UI is a sophisticated glassmorphism design system inspired by Apple's glass aesthetic. It creates a modern, elegant interface with translucent elements, subtle blur effects, and smooth animations.


## Core Design Principles


1. **Transparency & Blur**: Elements use semi-transparent backgrounds with backdrop blur effects
2. **Layered Depth**: Multiple glass layers create visual hierarchy
3. **Subtle Animations**: Smooth transitions and micro-interactions enhance user experience
4. **Consistent Border Radius**: Rounded corners create a soft, approachable feel
5. **Gradient Backgrounds**: Dynamic gradients add depth and visual interest


## Color System


### Primary Colors
```css
--galileo-bg-primary: #ECECEF;
--galileo-bg-secondary: #F3F4F6;
--galileo-bg-gradient-start: #F3F4F6;
--galileo-bg-gradient-end: #DFE2E8;
```


### Glass Effect Colors
```css
--galileo-glass-bg: rgba(255, 255, 255, 0.15);
--galileo-glass-bg-hover: rgba(255, 255, 255, 0.25);
--galileo-glass-border: rgba(255, 255, 255, 0.3);
--galileo-glass-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
--galileo-glass-blur: blur(20px);
```


### Advanced Glass Variations
```css
--galileo-glass-subtle-bg: rgba(255, 255, 255, 0.1);
--galileo-glass-elevated-bg: rgba(255, 255, 255, 0.25);
--galileo-glass-frosted-bg: rgba(255, 255, 255, 0.2);
--galileo-glass-refraction-bg: radial-gradient(circle at 20% 20%, rgba(255, 255, 255, 0.3) 0%, transparent 50%);
--galileo-glass-depth-bg: rgba(255, 255, 255, 0.15);
--galileo-glass-depth-border: rgba(255, 255, 255, 0.3);
```


### Text Colors
```css
--galileo-text-primary: #414753;
--galileo-text-secondary: #60616A;
--galileo-text-tertiary: #7A7E88;
```


### Interactive Elements
```css
--galileo-interactive-bg: rgba(255, 255, 255, 0.15);
--galileo-interactive-border: rgba(255, 255, 255, 0.3);
--galileo-interactive-hover: rgba(255, 255, 255, 0.25);
```


### Button Gradients
```css
--galileo-btn-gradient: var(--galileo-glass-bg);
--galileo-btn-gradient-hover: var(--galileo-glass-bg-hover);
```


## Component Classes


### Basic Glass Container
```css
.galileo-glass {
  background: var(--galileo-glass-bg);
  border-radius: 24px;
  box-shadow: var(--galileo-glass-shadow);
  backdrop-filter: var(--galileo-glass-blur);
  border: 1px solid var(--galileo-glass-border);
  transform: translateZ(0);
  will-change: transform, opacity;
}
```


### Glass Variations


#### Subtle Glass
```css
.galileo-glass-subtle {
  background: var(--galileo-glass-subtle-bg);
  border-radius: 16px;
  box-shadow: 0 2px 16px 0 rgba(0, 0, 0, 0.05);
  backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}
```


#### Elevated Glass
```css
.galileo-glass-elevated {
  background: var(--galileo-glass-elevated-bg);
  border-radius: 32px;
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.15);
  backdrop-filter: blur(25px);
  border: 1px solid rgba(255, 255, 255, 0.3);
}
```


#### Frosted Glass
```css
.galileo-glass-frosted {
  background:
    radial-gradient(circle at center, rgba(255, 255, 255, 0.3) 0%, rgba(255, 255, 255, 0.15) 70%, transparent 100%),
    var(--galileo-glass-frosted-bg);
  border-radius: 24px;
  box-shadow: var(--galileo-glass-shadow);
  backdrop-filter: var(--galileo-glass-blur);
  border: 1px solid var(--galileo-glass-border);
}
```


#### Refraction Glass
```css
.galileo-glass-refraction {
  background:
    var(--galileo-glass-refraction-bg),
    var(--galileo-glass-bg);
  border-radius: 24px;
  box-shadow: var(--galileo-glass-shadow);
  backdrop-filter: var(--galileo-glass-blur);
  border: 1px solid var(--galileo-glass-border);
}
```


#### Depth Glass
```css
.galileo-glass-depth {
  background: var(--galileo-glass-depth-bg);
  border-radius: 24px;
  box-shadow: var(--galileo-glass-depth-shadow);
  backdrop-filter: blur(20px);
  border: 1px solid var(--galileo-glass-depth-border);
  position: relative;
}


.galileo-glass-depth::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
}
```


### Button Styles


#### Primary Button
```css
.galileo-btn {
  background: var(--galileo-btn-gradient);
  border: none;
  color: white;
  border-radius: 50%;
  font-size: 16px;
  font-weight: 500;
  padding: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  transform: translateZ(0);
  will-change: transform, opacity;
}


.galileo-btn:hover {
  background: var(--galileo-btn-gradient-hover);
}
```


#### Depth Button
```css
.galileo-btn-depth {
  background: var(--galileo-glass-depth-bg);
  border: 1px solid var(--galileo-glass-depth-border);
  box-shadow:
    0 4px 30px rgba(0, 0, 0, 0.1),
    var(--galileo-glass-depth-inset);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}


.galileo-btn-depth:hover {
  background: var(--galileo-glass-elevated-bg);
  border-color: var(--galileo-glass-depth-border);
}
```


### Input Styles
```css
.galileo-input {
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  border-radius: 24px;
  padding: 12px 20px;
  font-size: 16px;
  transition: all 0.3s ease;
  backdrop-filter: blur(20px);
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
}


.galileo-input:focus {
  outline: none;
  border-color: rgba(255, 255, 255, 0.5);
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1), 0 0 0 2px rgba(255, 255, 255, 0.2);
}


.galileo-input-glow:focus {
  background: rgba(255, 255, 255, 0.15);
  box-shadow:
    0 0 0 2px rgba(45, 156, 219, 0.3),
    0 4px 30px rgba(0, 0, 0, 0.1);
}
```


### Panel with Edge Highlight
```css
.galileo-panel-highlight {
  position: relative;
  background: var(--galileo-glass-bg);
  border-radius: 24px;
  box-shadow: var(--galileo-glass-shadow);
  backdrop-filter: var(--galileo-glass-blur);
  border: 1px solid var(--galileo-glass-border);
}


.galileo-panel-highlight::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
}
```


### Modal Styles
```css
.galileo-modal-backdrop {
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(13px);
}


.galileo-modal {
  background: rgba(255, 255, 255, 0.74);
  backdrop-filter: blur(45px);
  border-radius: 32px;
  box-shadow: 0 8px 32px 0 rgba(100, 100, 100, 0.15);
  border: 1px solid rgba(200, 200, 200, 0.30);
  transform: scale(0.9);
  opacity: 0;
  transition: all 0.3s ease-out;
}


.galileo-modal.show {
  opacity: 1;
  transform: scale(1);
}
```


## Animation Effects


### Shimmer Effect
```css
.galileo-shimmer {
  position: relative;
  overflow: hidden;
}


.galileo-shimmer::after {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: var(--galileo-shimmer-gradient);
  animation: shimmer var(--galileo-shimmer-duration) ease-in-out infinite;
}


@keyframes shimmer {
  0% {
    left: -100%;
  }
  100% {
    left: 100%;
  }
}




### Background Animations
```css
@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(30px, -30px) scale(1.1); }
  66% { transform: translate(-20px, 20px) scale(0.9); }
}


@keyframes pulse {
  0%, 100% { transform: translate(-50%, -50%) scale(1); opacity: 0.2; }
  50% { transform: translate(-50%, -50%) scale(1.1); opacity: 0.3; }
}
```


## Typography


### Font Stack
```css
font-family: 'SF Pro Display', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
```


### Text Classes
```css
.galileo-text-primary {
  color: var(--galileo-text-primary);
}


.galileo-text-secondary {
  color: var(--galileo-text-secondary);
}


.galileo-text-tertiary {
  color: var(--galileo-text-tertiary);
}
```


## Implementation Guide


### 1. Setting Up the CSS Variables


First, define the CSS variables in your global stylesheet:


```css
:root {
  /* Galileo Glass UI Colors */
  --galileo-bg-primary: #ECECEF;
  --galileo-bg-secondary: #F3F4F6;
  --galileo-bg-gradient-start: #F3F4F6;
  --galileo-bg-gradient-end: #DFE2E8;
 
  /* Glassmorphism effect variables */
  --galileo-glass-bg: rgba(255, 255, 255, 0.15);
  --galileo-glass-bg-hover: rgba(255, 255, 255, 0.25);
  --galileo-glass-border: rgba(255, 255, 255, 0.3);
  --galileo-glass-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
  --galileo-glass-blur: blur(20px);
 
  /* Button gradient variables */
  --galileo-btn-gradient: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  --galileo-btn-gradient-hover: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);
 
  /* Text colors */
  --galileo-text-primary: #414753;
  --galileo-text-secondary: #60616A;
  --galileo-text-tertiary: #7A7E88;
 
  /* Interactive elements */
  --galileo-interactive-bg: rgba(255, 255, 255, 0.15);
  --galileo-interactive-border: rgba(255, 255, 255, 0.3);
  --galileo-interactive-hover: rgba(255, 255, 255, 0.25);
}
```


### 2. Setting Up the Body Background


```css
body {
  background: linear-gradient(135deg, var(--galileo-bg-gradient-start) 0%, var(--galileo-bg-gradient-end) 100%);
  font-family: 'SF Pro Display', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
  color: var(--galileo-text-primary);
  margin: 0;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  transition: background 0.3s ease;
}
```


### 3. Creating Glass Components


Use the predefined classes for consistent glassmorphism effects:


```html
<!-- Basic Glass Container -->
<div class="galileo-glass">
  <!-- Content here -->
</div>


<!-- Subtle Glass Container -->
<div class="galileo-glass-subtle">
  <!-- Content here -->
</div>


<!-- Elevated Glass Container -->
<div class="galileo-glass-elevated">
  <!-- Content here -->
</div>
```


### 4. Implementing Interactive Elements


```html
<!-- Glass Button -->
<button class="galileo-btn">
  Click me
</button>


<!-- Glass Input -->
<input class="galileo-input" type="text" placeholder="Enter text">


<!-- Glass Button with Depth -->
<button class="galileo-btn-depth">
  Click me
</button>
```


### 5. Adding Background Effects


For a more dynamic background, add floating elements:


```html
<div class="absolute inset-0 overflow-hidden">
  <div class="absolute -top-40 -right-40 w-80 h-80 rounded-full opacity-30" style={{
    background: 'var(--galileo-glass-refraction-bg)',
    filter: 'var(--galileo-glass-blur)',
    animation: 'float 20s ease-in-out infinite'
  }}></div>
  <div class="absolute -bottom-40 -left-40 w-80 h-80 rounded-full opacity-30" style={{
    background: 'var(--galileo-glass-refraction-bg)',
    filter: 'var(--galileo-glass-blur)',
    animation: 'float 25s ease-in-out infinite reverse'
  }}></div>
</div>
```


## Tailwind CSS Integration


If you're using Tailwind CSS, you can integrate the glassmorphism design system by adding the following to your `tailwind.config.js`:


```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        galileo: {
          'bg-primary': '#ECECEF',
          'bg-secondary': '#F3F4F6',
          'bg-gradient-start': '#F3F4F6',
          'bg-gradient-end': '#DFE2E8',
          'glass-bg': 'rgba(255, 255, 255, 0.15)',
          'glass-bg-hover': 'rgba(255, 255, 255, 0.25)',
          'glass-border': 'rgba(255, 255, 255, 0.3)',
          'text-primary': '#414753',
          'text-secondary': '#60616A',
          'text-tertiary': '#7A7E88',
          'interactive-bg': 'rgba(255, 255, 255, 0.15)',
          'interactive-border': 'rgba(255, 255, 255, 0.3)',
          'interactive-hover': 'rgba(255, 255, 255, 0.25)',
          'btn-gradient': 'linear-gradient(135deg, #2D9CDB 0%, #023f88 100%)',
          'btn-gradient-hover': 'linear-gradient(135deg, #023f88 0%, #2D9CDB 100%)',
          'glass-subtle-bg': 'rgba(255, 255, 255, 0.1)',
          'glass-elevated-bg': 'rgba(255, 255, 255, 0.25)',
          'glass-frosted-bg': 'rgba(255, 255, 255, 0.2)',
          'glass-depth-bg': 'rgba(255, 255, 255, 0.15)',
          'glass-depth-border': 'rgba(255, 255, 255, 0.3)',
        },
      },
      backdropBlur: {
        'galileo': '20px',
      },
      boxShadow: {
        'galileo': '0 4px 30px rgba(0, 0, 0, 0.1)',
      },
      borderRadius: {
        'galileo': '24px',
        'galileo-sm': '20px',
        'galileo-lg': '32px',
      },
    },
  },
}
```


## Browser Compatibility


For browsers that don't support backdrop-filter, add a fallback:


```css
@supports not (backdrop-filter: blur(1px)) {
  .galileo-glass {
    background: rgba(255, 255, 255, 0.9);
  }
}
```


## Performance Optimization


To ensure smooth performance with glassmorphism effects:


1. Use `transform: translateZ(0)` and `will-change: transform, opacity` for animated elements
2. Limit the number of glass elements on a single page
3. Use hardware acceleration where possible
4. Optimize blur values for performance (15-25px is a good range)


## Customization Tips


1. **Adjust Transparency**: Modify the alpha values in the rgba colors to make elements more or less transparent
2. **Change Blur Intensity**: Adjust the blur value in the backdrop-filter property
3. **Customize Colors**: Replace the color values to match your brand
4. **Modify Border Radius**: Adjust the border-radius values for different visual styles
5. **Add Your Own Gradients**: Create custom gradient backgrounds for unique effects


## Example Implementation


Here's a complete example of a login page using the Galileo Glass UI design system:


```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Glassmorphism Login</title>
  <style>
    /* Include all the CSS variables and classes from above */
  </style>
</head>
<body>
  <div class="min-h-screen flex items-center justify-center relative overflow-hidden" style={{
    background: 'linear-gradient(135deg, var(--galileo-bg-gradient-start) 0%, var(--galileo-bg-gradient-end) 100%)'
  }}>
    <!-- Animated background elements -->
    <div class="absolute inset-0 overflow-hidden">
      <div class="absolute -top-40 -right-40 w-80 h-80 rounded-full opacity-30" style={{
        background: 'var(--galileo-glass-refraction-bg)',
        filter: 'var(--galileo-glass-blur)',
        animation: 'float 20s ease-in-out infinite'
      }}></div>
      <div class="absolute -bottom-40 -left-40 w-80 h-80 rounded-full opacity-30" style={{
        background: 'var(--galileo-glass-refraction-bg)',
        filter: 'var(--galileo-glass-blur)',
        animation: 'float 25s ease-in-out infinite reverse'
      }}></div>
    </div>
   
    <!-- Glassmorphism overlay -->
    <div class="absolute inset-0" style={{
      background: 'linear-gradient(to bottom, var(--galileo-glass-subtle-bg) 0%, var(--galileo-glass-bg) 100%)',
      backdropFilter: 'var(--galileo-glass-blur)'
    }}></div>


    <!-- Login Form -->
    <div class="max-w-md w-full space-y-8 galileo-glass p-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold galileo-text-primary">
          Sign in to your account
        </h2>
      </div>
     
      <form class="mt-8 space-y-6">
        <div>
          <label for="email" class="block text-sm font-medium galileo-text-primary">
            Email address
          </label>
          <div class="mt-1">
            <input
              id="email"
              name="email"
              type="email"
              required
              class="galileo-input w-full"
              placeholder="Enter your email"
            />
          </div>
        </div>


        <div>
          <label for="password" class="block text-sm font-medium galileo-text-primary">
            Password
          </label>
          <div class="mt-1">
            <input
              id="password"
              name="password"
              type="password"
              required
              class="galileo-input w-full"
              placeholder="Enter your password"
            />
          </div>
        </div>


        <div>
          <button type="submit" class="galileo-btn-depth w-full py-3 px-4">
            Sign in
          </button>
        </div>
      </form>
    </div>
  </div>
</body>
</html>
```


This design system provides a comprehensive foundation for creating beautiful, modern glassmorphism interfaces that can be easily adapted to any brand application.


/* Galileo Glass UI - Apple Glass Style Design System */


/* CSS Variables */
:root {
  /* Galileo Glass UI Colors */
  --galileo-bg-primary: #ECECEF;
  --galileo-bg-secondary: #F3F4F6;
  --galileo-bg-gradient-start: #F3F4F6;
  --galileo-bg-gradient-end: #DFE2E8;
 
  /* Glassmorphism effect variables */
  --galileo-glass-bg: rgba(255, 255, 255, 0.15);
  --galileo-glass-bg-hover: rgba(255, 255, 255, 0.25);
  --galileo-glass-border: rgba(255, 255, 255, 0.3);
  --galileo-glass-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
  --galileo-glass-blur: blur(20px);
 
  /* Button gradient variables */
  --galileo-btn-gradient: var(--galileo-glass-bg);
  --galileo-btn-gradient-hover: var(--galileo-glass-bg-hover);
 
  /* Advanced Glassmorphism Variables */
  --galileo-glass-subtle-bg: rgba(255, 255, 255, 0.1);
  --galileo-glass-elevated-bg: rgba(255, 255, 255, 0.25);
  --galileo-glass-frosted-bg: rgba(255, 255, 255, 0.2);
  --galileo-glass-refraction-bg: radial-gradient(circle at 20% 20%, rgba(255, 255, 255, 0.3) 0%, transparent 50%);
  --galileo-glass-depth-bg: rgba(255, 255, 255, 0.15);
  --galileo-glass-depth-border: rgba(255, 255, 255, 0.3);
  --galileo-glass-depth-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
  --galileo-glass-depth-inset: inset 0 1px 0 rgba(255, 255, 255, 0.3);
 
  /* Text colors */
  --galileo-text-primary: #414753;
  --galileo-text-secondary: #60616A;
  --galileo-text-tertiary: #7A7E88;
 
  /* Interactive elements */
  --galileo-interactive-bg: rgba(255, 255, 255, 0.15);
  --galileo-interactive-border: rgba(255, 255, 255, 0.3);
  --galileo-interactive-hover: rgba(255, 255, 255, 0.25);
 
  /* Animation variables */
  --galileo-shimmer-gradient: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  --galileo-shimmer-duration: 3s;
}


/* Base Styles */
body {
  background: linear-gradient(135deg, var(--galileo-bg-gradient-start) 0%, var(--galileo-bg-gradient-end) 100%);
  font-family: 'SF Pro Display', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
  color: var(--galileo-text-primary);
  margin: 0;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  transition: background 0.3s ease;
}


/* Glass Components */
.galileo-glass {
  background: var(--galileo-glass-bg);
  border-radius: 24px;
  box-shadow: var(--galileo-glass-shadow);
  backdrop-filter: var(--galileo-glass-blur);
  border: 1px solid var(--galileo-glass-border);
  transform: translateZ(0);
  will-change: transform, opacity;
}


.galileo-glass-hover {
  background: var(--galileo-glass-bg-hover);
}


/* Glass Variations */
.galileo-glass-subtle {
  background: var(--galileo-glass-subtle-bg);
  border-radius: 16px;
  box-shadow: 0 2px 16px 0 rgba(0, 0, 0, 0.05);
  backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}


.galileo-glass-elevated {
  background: var(--galileo-glass-elevated-bg);
  border-radius: 32px;
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.15);
  backdrop-filter: blur(25px);
  border: 1px solid rgba(255, 255, 255, 0.3);
}


.galileo-glass-frosted {
  background:
    radial-gradient(circle at center, rgba(255, 255, 255, 0.3) 0%, rgba(255, 255, 255, 0.15) 70%, transparent 100%),
    var(--galileo-glass-frosted-bg);
  border-radius: 24px;
  box-shadow: var(--galileo-glass-shadow);
  backdrop-filter: var(--galileo-glass-blur);
  border: 1px solid var(--galileo-glass-border);
}


.galileo-glass-refraction {
  background:
    var(--galileo-glass-refraction-bg),
    var(--galileo-glass-bg);
  border-radius: 24px;
  box-shadow: var(--galileo-glass-shadow);
  backdrop-filter: var(--galileo-glass-blur);
  border: 1px solid var(--galileo-glass-border);
}


.galileo-glass-depth {
  background: var(--galileo-glass-depth-bg);
  border-radius: 24px;
  box-shadow: var(--galileo-glass-depth-shadow);
  backdrop-filter: blur(20px);
  border: 1px solid var(--galileo-glass-depth-border);
  position: relative;
}


.galileo-glass-depth::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
}


/* Button Styles */
.galileo-btn {
  background: var(--galileo-btn-gradient);
  border: none;
  color: white;
  border-radius: 50%;
  font-size: 16px;
  font-weight: 500;
  padding: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  transform: translateZ(0);
  will-change: transform, opacity;
}


.galileo-btn:hover {
  background: var(--galileo-btn-gradient-hover);
}


.galileo-btn-depth {
  background: var(--galileo-glass-depth-bg);
  border: 1px solid var(--galileo-glass-depth-border);
  box-shadow:
    0 4px 30px rgba(0, 0, 0, 0.1),
    var(--galileo-glass-depth-inset);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  color: var(--galileo-text-primary);
  border-radius: 24px;
  padding: 12px 20px;
  font-size: 15px;
}


.galileo-btn-depth:hover {
  background: var(--galileo-glass-elevated-bg);
  border-color: var(--galileo-glass-depth-border);
}


/* Input Styles */
.galileo-input {
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: var(--galileo-text-primary);
  border-radius: 24px;
  padding: 12px 20px;
  font-size: 16px;
  transition: all 0.3s ease;
  backdrop-filter: blur(20px);
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
  width: 100%;
}


.galileo-input:focus {
  outline: none;
  border-color: rgba(255, 255, 255, 0.5);
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1), 0 0 0 2px rgba(255, 255, 255, 0.2);
}


.galileo-input-glow:focus {
  background: rgba(255, 255, 255, 0.15);
  box-shadow:
    0 0 0 2px rgba(45, 156, 219, 0.3),
    0 4px 30px rgba(0, 0, 0, 0.1);
}


/* Text Styles */
.galileo-text-primary {
  color: var(--galileo-text-primary);
}


.galileo-text-secondary {
  color: var(--galileo-text-secondary);
}


.galileo-text-tertiary {
  color: var(--galileo-text-tertiary);
}


/* Icon System */
.galileo-icon {
  stroke: currentColor;
  stroke-width: 2px;
  fill: none;
  stroke-linecap: round;
  stroke-linejoin: round;
}


.galileo-icon-filled {
  fill: currentColor;
  stroke: none;
}


/* Animation Effects */
.galileo-shimmer {
  position: relative;
  overflow: hidden;
}


.galileo-shimmer::after {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: var(--galileo-shimmer-gradient);
  animation: shimmer var(--galileo-shimmer-duration) ease-in-out infinite;
}


@keyframes shimmer {
  0% {
    left: -100%;
  }
  100% {
    left: 100%;
  }
}


/* Panel with Edge Highlight */
.galileo-panel-highlight {
  position: relative;
  background: var(--galileo-glass-bg);
  border-radius: 24px;
  box-shadow: var(--galileo-glass-shadow);
  backdrop-filter: var(--galileo-glass-blur);
  border: 1px solid var(--galileo-glass-border);
}


.galileo-panel-highlight::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
}


/* Modal with Backdrop */
.galileo-modal-backdrop {
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(13px);
}


.galileo-modal {
  background: rgba(255, 255, 255, 0.74);
  backdrop-filter: blur(45px);
  border-radius: 32px;
  box-shadow: 0 8px 32px 0 rgba(100, 100, 100, 0.15);
  border: 1px solid rgba(200, 200, 200, 0.30);
  transform: scale(0.9);
  opacity: 0;
  transition: all 0.3s ease-out;
}


.galileo-modal.show {
  opacity: 1;
  transform: scale(1);
}


/* Background Animations */
@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(30px, -30px) scale(1.1); }
  66% { transform: translate(-20px, 20px) scale(0.9); }
}


@keyframes pulse {
  0%, 100% { transform: translate(-50%, -50%) scale(1); opacity: 0.2; }
  50% { transform: translate(-50%, -50%) scale(1.1); opacity: 0.3; }
}


/* Performance Optimizations */
.galileo-optimized {
  transform: translateZ(0);
  will-change: transform, opacity;
}


/* Browser Compatibility */
@supports not (backdrop-filter: blur(1px)) {
  .galileo-glass {
    background: rgba(255, 255, 255, 0.9);
  }
}


# LibreChat CSS Styles Documentation


This document provides a comprehensive guide to the CSS styles used in LibreChat, focusing on the key components: login, register, page, sidebar, chat, and input. These styles are designed with a modern glassmorphism aesthetic inspired by Apple's design language.


## Table of Contents
1. [Core Design System](#core-design-system)
2. [Color Variables](#color-variables)
3. [Glassmorphism Effects](#glassmorphism-effects)
4. [Component Styles](#component-styles)
5. [Responsive Design](#responsive-design)
6. [Animation Effects](#animation-effects)
7. [Implementation Guide](#implementation-guide)


## Core Design System


The design system is built around the "Galileo Glass UI" concept, which emphasizes:
- Glassmorphism effects with backdrop blur
- Subtle gradients and shadows
- Smooth transitions and micro-interactions
- Consistent border radius values
- A cohesive color palette


### Base Styles


```css
/* Base body styling */
body {
  background: linear-gradient(135deg, var(--galileo-bg-gradient-start) 0%, var(--galileo-bg-gradient-end) 100%);
  font-family: 'SF Pro Display', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
  color: var(--galileo-text-primary);
  margin: 0;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  transition: background 0.3s ease;
}
```


## Color Variables


The color system is defined using CSS custom properties for easy theming and brand customization:


```css
:root {
  /* Background Colors */
  --galileo-bg-primary: #ECECEF;
  --galileo-bg-secondary: #F3F4F6;
  --galileo-bg-gradient-start: #F3F4F6;
  --galileo-bg-gradient-end: #DFE2E8;
 
  /* Glassmorphism Effect Variables */
  --galileo-glass-bg: rgba(255, 255, 255, 0.15);
  --galileo-glass-bg-hover: rgba(255, 255, 255, 0.25);
  --galileo-glass-border: rgba(255, 255, 255, 0.3);
  --galileo-glass-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
  --galileo-glass-blur: blur(20px);
 
  /* Button Gradient Variables */
  --galileo-btn-gradient: linear-gradient(135deg, #2D9CDB 0%, #023f88   100%);
  --galileo-btn-gradient-hover: linear-gradient(135deg, #023f88   0%, #2D9CDB 100%);
 
  /* Advanced Glassmorphism Variables */
  --galileo-glass-subtle-bg: rgba(255, 255, 255, 0.1);
  --galileo-glass-elevated-bg: rgba(255, 255, 255, 0.25);
  --galileo-glass-frosted-bg: rgba(255, 255, 255, 0.2);
  --galileo-glass-refraction-bg: radial-gradient(circle at 20% 20%, rgba(255, 255, 255, 0.3) 0%, transparent 50%);
  --galileo-glass-depth-bg: rgba(255, 255, 255, 0.15);
  --galileo-glass-depth-border: rgba(255, 255, 255, 0.3);
  --galileo-glass-depth-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
  --galileo-glass-depth-inset: inset 0 1px 0 rgba(255, 255, 255, 0.3);
 
  /* Text Colors */
  --galileo-text-primary: #414753;
  --galileo-text-secondary: #60616A;
  --galileo-text-tertiary: #7A7E88;
 
  /* Interactive Elements */
  --galileo-interactive-bg: rgba(255, 255, 255, 0.15);
  --galileo-interactive-border: rgba(255, 255, 255, 0.3);
  --galileo-interactive-hover: rgba(255, 255, 255, 0.25);
 
  /* Animation Variables */
  --galileo-shimmer-gradient: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  --galileo-shimmer-duration: 3s;
}
```


## Glassmorphism Effects


The glassmorphism effect is the core of the design system:


### Standard Glass Effect
```css
.galileo-glass {
  background: var(--galileo-glass-bg);
  border-radius: 24px;
  box-shadow: var(--galileo-glass-shadow);
  backdrop-filter: var(--galileo-glass-blur);
  border: 1px solid var(--galileo-glass-border);
  transform: translateZ(0);
  will-change: transform, opacity;
}
```


### Glass Hover Effect
```css
.galileo-glass-hover {
  background: var(--galileo-glass-bg-hover);
}
```


### Glass Variations


#### Subtle Glass
```css
.galileo-glass-subtle {
  background: var(--galileo-glass-subtle-bg);
  border-radius: 16px;
  box-shadow: 0 2px 16px 0 rgba(0, 0, 0, 0.05);
  backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}
```


#### Elevated Glass
```css
.galileo-glass-elevated {
  background: var(--galileo-glass-elevated-bg);
  border-radius: 32px;
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.15);
  backdrop-filter: blur(25px);
  border: 1px solid rgba(255, 255, 255, 0.3);
}
```


#### Frosted Glass
```css
.galileo-glass-frosted {
  background:
    radial-gradient(circle at center, rgba(255, 255, 255, 0.3) 0%, rgba(255, 255, 255, 0.15) 70%, transparent 100%),
    var(--galileo-glass-frosted-bg);
  border-radius: 24px;
  box-shadow: var(--galileo-glass-shadow);
  backdrop-filter: var(--galileo-glass-blur);
  border: 1px solid var(--galileo-glass-border);
}
```


#### Refraction Glass
```css
.galileo-glass-refraction {
  background:
    var(--galileo-glass-refraction-bg),
    var(--galileo-glass-bg);
  border-radius: 24px;
  box-shadow: var(--galileo-glass-shadow);
  backdrop-filter: var(--galileo-glass-blur);
  border: 1px solid var(--galileo-glass-border);
}
```


#### Depth Glass
```css
.galileo-glass-depth {
  background: var(--galileo-glass-depth-bg);
  border-radius: 24px;
  box-shadow: var(--galileo-glass-depth-shadow);
  backdrop-filter: blur(20px);
  border: 1px solid var(--galileo-glass-depth-border);
  position: relative;
}


.galileo-glass-depth::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
}
```


## Component Styles


### Login & Register Pages


The authentication pages use a centered layout with glassmorphism effects:


```css
.auth-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, var(--galileo-bg-gradient-start) 0%, var(--galileo-bg-gradient-end) 100%);
}


.auth-form-container {
  max-width: 28rem;
  width: 100%;
  background: var(--galileo-glass-bg);
  backdrop-filter: var(--galileo-glass-blur);
  border: 1px solid var(--galileo-glass-border);
  border-radius: 20px;
  box-shadow: var(--galileo-glass-shadow);
  padding: 2rem;
}


.auth-input {
  background: var(--galileo-interactive-bg);
  backdrop-filter: var(--galileo-glass-blur);
  border: 1px solid var(--galileo-interactive-border);
  border-radius: 20px;
  box-shadow: var(--galileo-glass-shadow);
  color: var(--galileo-text-primary);
  font-size: 15px;
  padding: 12px 20px;
  transition: all 0.25s ease;
}


.auth-input:focus {
  outline: none;
  border-color: rgba(255, 255, 255, 0.5);
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1), 0 0 0 2px rgba(255, 255, 255, 0.2);
}


.auth-button {
  background: var(--galileo-interactive-bg);
  border: 1px solid var(--galileo-interactive-border);
  border-radius: 20px;
  box-shadow: var(--galileo-glass-shadow);
  color: var(--galileo-text-primary);
  font-size: 15px;
  padding: 12px 20px;
  transition: all 0.25s ease;
}


.auth-button:hover {
  background: var(--galileo-interactive-hover);
}
```


### Animated Background Elements


The authentication pages include animated background elements:


```css
.auth-bg-element {
  position: absolute;
  border-radius: 50%;
  opacity: 0.3;
  background: var(--galileo-glass-refraction-bg);
  filter: var(--galileo-glass-blur);
}


.auth-bg-element-1 {
  top: -10rem;
  right: -10rem;
  width: 20rem;
  height: 20rem;
  animation: float 20s ease-in-out infinite;
}


.auth-bg-element-2 {
  bottom: -10rem;
  left: -10rem;
  width: 20rem;
  height: 20rem;
  animation: float 25s ease-in-out infinite reverse;
}


.auth-bg-element-3 {
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 24rem;
  height: 24rem;
  opacity: 0.2;
  filter: blur(60px);
  animation: pulse 10s ease-in-out infinite;
}


.auth-glass-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to bottom, var(--galileo-glass-subtle-bg) 0%, var(--galileo-glass-bg) 100%);
  backdrop-filter: var(--galileo-glass-blur);
}
```


### Sidebar Component


The sidebar uses a glassmorphism effect with subtle interactions:


```css
.sidebar {
  width: 100%;
  width: 16rem;
  padding: 0.75rem 1rem;
  display: flex;
  flex-direction: column;
  height: 100%;
  transition: color 0.3s ease;
}


.sidebar-search-input {
  width: 100%;
  padding-left: 2.25rem;
  padding-right: 3rem;
  padding-top: 0.75rem;
  padding-bottom: 0.75rem;
  font-size: 0.875rem;
  border-radius: 0.75rem;
  background: var(--galileo-interactive-bg);
  backdrop-filter: var(--galileo-glass-blur);
  border: 1px solid var(--galileo-interactive-border);
  color: var(--galileo-text-primary);
  transition: all 0.25s ease;
}


.sidebar-new-chat-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  width: 100%;
  padding: 0.75rem;
  margin-bottom: 0.75rem;
  font-size: 0.875rem;
  font-weight: 500;
  border-radius: 0.75rem;
  background: var(--galileo-interactive-bg);
  backdrop-filter: var(--galileo-glass-blur);
  border: 1px solid var(--galileo-interactive-border);
  box-shadow: var(--galileo-glass-shadow);
  color: var(--galileo-text-primary);
  transition: all 0.25s ease;
}


.sidebar-new-chat-button:hover {
  background: var(--galileo-interactive-hover);
}


.sidebar-conversation-item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  border-radius: 0.75rem;
  font-size: 0.875rem;
  transition: all 0.2s ease;
  background: transparent;
  border: 1px solid transparent;
  color: var(--galileo-text-secondary);
}


.sidebar-conversation-item:hover {
  background: var(--galileo-interactive-bg);
  border: 1px solid var(--galileo-interactive-border);
}


.sidebar-conversation-item.active {
  background: var(--galileo-interactive-hover);
  border: 1px solid var(--galileo-interactive-border);
  color: var(--galileo-text-primary);
  font-weight: 500;
}
```


### Chat Component


The chat interface uses glassmorphism for messages and input areas:


```css
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  transition: color 0.3s ease;
  position: relative;
}


.chat-message {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  margin-bottom: 1rem;
}


.chat-message.user {
  justify-content: flex-end;
}


.chat-message.ai {
  justify-content: flex-start;
}


.chat-message-content {
  max-width: 28rem;
  padding: 0.75rem;
  font-size: 0.875rem;
  border-radius: 1rem;
  position: relative;
}


.chat-message.user .chat-message-content {
  background: rgba(243, 244, 246, 0.6);
  backdrop-filter: var(--galileo-glass-blur);
  color: var(--galileo-text-primary);
  border-bottom-right-radius: 0;
}


.chat-message.ai .chat-message-content {
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: var(--galileo-glass-blur);
  border: 1px solid rgba(229, 231, 235, 0.6);
  color: var(--galileo-text-primary);
  border-bottom-left-radius: 0;
}


.chat-input-container {
  position: relative;
  margin-top: auto;
  padding-top: 0.75rem;
}


.chat-input {
  width: 100%;
  padding: 0.75rem;
  padding-left: 2.5rem;
  padding-right: 5rem;
  font-size: 0.875rem;
  border-radius: 0.75rem;
  background: rgba(243, 244, 246, 0.6);
  backdrop-filter: var(--galileo-glass-blur);
  border: 1px solid rgba(229, 231, 235, 0.6);
  color: var(--galileo-text-primary);
  transition: all 0.25s ease;
}


.chat-input:focus {
  outline: none;
  border-color: rgba(209, 213, 219, 0.6);
  box-shadow: 0 0 0 2px rgba(209, 213, 219, 0.3);
}


.chat-send-button {
  position: absolute;
  top: 50%;
  right: 0.625rem;
  transform: translateY(-50%);
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.5rem;
  background: rgba(31, 41, 55, 0.6);
  backdrop-filter: var(--galileo-glass-blur);
  color: white;
  transition: all 0.2s ease;
}


.chat-send-button:hover {
  background: rgba(31, 41, 55, 0.8);
}
```


### Voice Call Component


The voice call interface uses glassmorphism for the modal and controls:


```css
.voice-call-modal {
  position: fixed;
  inset: 0;
  z-index: 50;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(10px);
}


.voice-call-modal.light {
  background: rgba(255, 255, 255, 0.7);
}


.voice-call-modal.dark {
  background: rgba(0, 0, 0, 0.8);
}


.voice-call-close-button {
  position: absolute;
  top: 1.5rem;
  right: 1.5rem;
  padding: 0.75rem;
  border-radius: 50%;
  transition: all 0.2s ease;
}


.voice-call-close-button.light {
  background: rgba(243, 244, 246, 0.8);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(0, 0, 0, 0.1);
  color: rgb(75 85 99);
}


.voice-call-close-button.dark {
  background: rgba(31, 41, 55, 0.85);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: rgb(209 213 219);
}


.voice-call-close-button:hover {
  opacity: 0.8;
}


.voice-call-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2rem;
}


.voice-call-visualization {
  position: relative;
}


.voice-call-circle {
  width: 12rem;
  height: 12rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}


.voice-call-circle.listening {
  background: rgba(59, 130, 246, 0.4);
  animation: pulse 2s infinite;
}


.voice-call-circle.speaking {
  background: rgba(34, 197, 94, 0.4);
  animation: pulse 2s infinite;
}


.voice-call-circle.connected {
  background: rgba(107, 114, 128, 0.3);
}


.voice-call-circle.connecting {
  background: rgba(245, 158, 11, 0.4);
  animation: pulse 2s infinite;
}


.voice-call-waves {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}


.voice-call-wave {
  width: 0.5rem;
  border-radius: 9999px;
  transition: all 0.3s ease;
}


.voice-call-wave.light {
  background: rgb(37 99 235);
}


.voice-call-wave.dark {
  background: rgb(96 165 250);
}


.voice-call-wave.active {
  animation: wave 1s ease-in-out infinite;
}


.voice-call-wave.reverse {
  animation: wave-reverse 1s ease-in-out infinite;
}


.voice-call-status {
  text-align: center;
}


.voice-call-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}


.voice-call-title.light {
  color: rgb(17 24 39);
}


.voice-call-title.dark {
  color: rgb(243 244 246);
}


.voice-call-status-text {
  font-size: 1.125rem;
}


.voice-call-status-text.connecting {
  color: rgb(245 158 11);
}


.voice-call-status-text.connected.light {
  color: rgb(107 114 128);
}


.voice-call-status-text.connected.dark {
  color: rgb(156 163 175);
}


.voice-call-status-text.listening {
  color: rgb(59 130 246);
}


.voice-call-status-text.speaking {
  color: rgb(34 197, 94);
}


.voice-call-mute-button {
  padding: 1.5rem;
  border-radius: 50%;
  transition: all 0.2s ease;
  box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}


.voice-call-mute-button.muted.light {
  background: rgba(239, 68, 68, 0.8);
  color: white;
}


.voice-call-mute-button.muted.dark {
  background: rgba(220, 38, 38, 0.85);
  color: white;
}


.voice-call-mute-button.muted:hover.light {
  background: rgba(220, 38, 38, 0.8);
}


.voice-call-mute-button.muted:hover.dark {
  background: rgba(185, 28, 28, 0.85);
}


.voice-call-mute-button.unmuted.light {
  background: rgba(31, 41, 55, 0.85);
  color: rgb(209 213 219);
}


.voice-call-mute-button.unmuted.dark {
  background: rgba(55, 65, 81, 0.85);
  color: rgb(156 163 175);
}


.voice-call-mute-button.unmuted:hover.light {
  background: rgba(55, 65, 81, 0.85);
}


.voice-call-mute-button.unmuted:hover.dark {
  background: rgba(75, 85, 99, 0.85);
}


.voice-call-mute-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}


.voice-call-mute-icon {
  position: relative;
}


.voice-call-mute-line {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}


.voice-call-transcript {
  max-width: 42rem;
  max-height: 12rem;
  overflow-y: auto;
  padding: 1rem;
  border-radius: 0.5rem;
  gap: 0.5rem;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}


.voice-call-transcript.light {
  background: rgba(31, 41, 55, 0.85);
}


.voice-call-transcript.dark {
  background: rgba(243, 244, 246, 0.8);
}


.voice-call-transcript-item {
  gap: 0.25rem;
}


.voice-call-transcript-user {
  font-size: 0.875rem;
  color: rgb(37 99 235);
}


.voice-call-transcript-ai {
  font-size: 0.875rem;
  color: rgb(34 197, 94);
}


/* Voice Wave Animations */
@keyframes wave {
  0%, 100% {
    height: 20px;
  }
  50% {
    height: 60px;
  }
}


@keyframes wave-reverse {
  0%, 100% {
    height: 60px;
  }
  50% {
    height: 20px;
  }
}
```


### Input Component


The input component uses a consistent glassmorphism style:


```css
.galileo-input {
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  border-radius: 24px;
  padding: 12px 20px;
  font-size: 16px;
  transition: all 0.3s ease;
  backdrop-filter: blur(20px);
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
}


.galileo-input:focus {
  outline: none;
  border-color: rgba(255, 255, 255, 0.5);
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1), 0 0 0 2px rgba(255, 255, 255, 0.2);
}


.galileo-input-glow:focus {
  background: rgba(255, 255, 255, 0.15);
  box-shadow:
    0 0 0 2px rgba(45, 156, 219, 0.3),
    0 4px 30px rgba(0, 0, 0, 0.1);
}
```


## Responsive Design


The design system includes responsive breakpoints and adjustments:


```css
/* Mobile adjustments */
@media (max-width: 1023px) {
  header.fixed {
    width: 100vw !important;
    max-width: 100vw !important;
  }
}


/* Mobile menu button */
.mobile-menu-button {
  display: none;
}


@media (max-width: 1023px) {
  .mobile-menu-button {
    display: flex;
    position: fixed;
    top: 1rem;
    left: 1rem;
    z-index: 50;
    width: 3rem;
    height: 3rem;
    border-radius: 50%;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
  }
}


/* Sidebar adjustments */
@media (max-width: 1023px) {
  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    height: 100vh;
    width: 80%;
    max-width: 20rem;
    z-index: 40;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
  }
 
  .sidebar.open {
    transform: translateX(0);
  }
}
```


## Animation Effects


The design system includes several animation effects:


### Float Animation
```css
@keyframes float {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  33% {
    transform: translate(30px, -30px) scale(1.1);
  }
  66% {
    transform: translate(-20px, 20px) scale(0.9);
  }
}
```


### Pulse Animation
```css
@keyframes pulse {
  0%, 100% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 0.2;
  }
  50% {
    transform: translate(-50%, -50%) scale(1.1);
    opacity: 0.3;
  }
}
```


### Shimmer Effect
```css
.galileo-shimmer {
  position: relative;
  overflow: hidden;
}


.galileo-shimmer::after {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: var(--galileo-shimmer-gradient);
  animation: shimmer var(--galileo-shimmer-duration) ease-in-out infinite;
}


@keyframes shimmer {
  0% {
    left: -100%;
  }
  100% {
    left: 100%;
  }
}
```


### Slide In Animation
```css
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}


.animate-slide-in {
  animation: slideIn 0.3s ease-out;
}
```


### Fade In Animation
```css
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}


.animate-fade-in {
  animation: fadeIn 0.5s ease-out;
}
```


## Implementation Guide


### 1. Basic Setup


To implement these styles in your project:


1. Include the CSS variables in your root stylesheet:
```css
:root {
  /* Include all the CSS variables from the Color Variables section */
}
```


2. Add the base styles:
```css
body {
  background: linear-gradient(135deg, var(--galileo-bg-gradient-start) 0%, var(--galileo-bg-gradient-end) 100%);
  font-family: 'SF Pro Display', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
  color: var(--galileo-text-primary);
  margin: 0;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  transition: background 0.3s ease;
}
```


### 2. Component Implementation


For each component, apply the appropriate classes:


#### Login/Register Page
```html
<div class="auth-container">
  <!-- Animated background elements -->
  <div class="auth-bg-element auth-bg-element-1"></div>
  <div class="auth-bg-element auth-bg-element-2"></div>
  <div class="auth-bg-element auth-bg-element-3"></div>
 
  <!-- Glass overlay -->
  <div class="auth-glass-overlay"></div>
 
  <!-- Form container -->
  <div class="auth-form-container">
    <form>
      <input type="email" class="auth-input" placeholder="Email">
      <input type="password" class="auth-input" placeholder="Password">
      <button type="submit" class="auth-button">Sign In</button>
    </form>
  </div>
</div>
```


#### Sidebar
```html
<aside class="sidebar">
  <input type="text" class="sidebar-search-input" placeholder="Search">
  <button class="sidebar-new-chat-button">New Chat</button>
  <nav>
    <ul>
      <li>
        <button class="sidebar-conversation-item">Conversation 1</button>
      </li>
      <li>
        <button class="sidebar-conversation-item active">Conversation 2</button>
      </li>
    </ul>
  </nav>
</aside>
```


#### Chat Interface
```html
<div class="chat-container">
  <div class="chat-messages">
    <div class="chat-message user">
      <div class="chat-message-content">User message</div>
    </div>
    <div class="chat-message ai">
      <div class="chat-message-content">AI response</div>
    </div>
  </div>
  <div class="chat-input-container">
    <input type="text" class="chat-input" placeholder="Type a message...">
    <button class="chat-send-button">Send</button>
  </div>
</div>
```


#### Voice Call Interface
```html
<div class="voice-call-modal">
  <div class="voice-call-card">
    <!-- Close button -->
    <button class="voice-call-close-button">
      <svg><!-- X icon --></svg>
    </button>
   
    <!-- Main content -->
    <div class="voice-call-content">
      <!-- Voice wave visualization -->
      <div class="voice-call-visualization">
        <div class="voice-call-circle">
          <div class="voice-call-waves">
            <div class="voice-call-wave"></div>
            <div class="voice-call-wave"></div>
            <div class="voice-call-wave"></div>
            <div class="voice-call-wave"></div>
            <div class="voice-call-wave"></div>
          </div>
        </div>
      </div>
     
      <!-- Status text -->
      <div class="voice-call-status">
        <h2 class="voice-call-title">AI Voice Call</h2>
        <p class="voice-call-status-text">Ready to talk</p>
      </div>
     
      <!-- Mute button -->
      <button class="voice-call-mute-button">
        <div class="voice-call-mute-icon">
          <svg><!-- Microphone icon --></svg>
          <div class="voice-call-mute-line">
            <div class="w-10 h-0.5 bg-white transform rotate-45"></div>
          </div>
        </div>
      </button>
     
      <!-- Transcript -->
      <div class="voice-call-transcript">
        <div class="voice-call-transcript-item">
          <p class="voice-call-transcript-user"><strong>You:</strong> Hello</p>
          <p class="voice-call-transcript-ai"><strong>AI:</strong> Hi there!</p>
        </div>
      </div>
    </div>
  </div>
</div>
```


### 3. Customization for Different Brands


To adapt these styles for different brands:


1. Update the color variables:
```css
:root {
  /* Brand-specific colors */
  --brand-primary: #YOUR_BRAND_COLOR;
  --brand-secondary: #YOUR_SECONDARY_COLOR;
 
  /* Update glassmorphism variables to match brand */
  --galileo-btn-gradient: linear-gradient(135deg, var(--brand-primary) 0%, var(--brand-secondary) 100%);
  --galileo-btn-gradient-hover: linear-gradient(135deg, var(--brand-secondary) 0%, var(--brand-primary) 100%);
}
```


2. Adjust border radius values if needed:
```css
:root {
  --border-radius-sm: 8px;
  --border-radius-md: 16px;
  --border-radius-lg: 24px;
  --border-radius-xl: 32px;
}
```


3. Modify animation durations for different brand personalities:
```css
:root {
  --animation-fast: 0.15s;
  --animation-normal: 0.25s;
  --animation-slow: 0.5s;
}
```


### 4. Browser Compatibility


For browsers that don't support backdrop-filter, include a fallback:


```css
@supports not (backdrop-filter: blur(1px)) {
  .galileo-glass {
    background: rgba(255, 255, 255, 0.9);
  }
}
```


### 5. Performance Optimization


To ensure smooth performance:


1. Use transform and opacity for animations:
```css
.galileo-optimized {
  transform: translateZ(0);
  will-change: transform, opacity;
}
```


2. Apply hardware acceleration to glassmorphism elements:
```css
.galileo-glass {
  transform: translateZ(0);
  will-change: transform, opacity;
}
```


## Conclusion


This CSS style system provides a comprehensive foundation for building modern, glassmorphic interfaces inspired by Apple's design language. By using the CSS variables and component classes outlined in this document, you can easily create consistent, beautiful interfaces that can be customized for different brands while maintaining the core design principles.


The key advantages of this system are:
- Consistent design language across components
- Easy theming and brand customization
- Smooth animations and micro-interactions
- Responsive design that works across devices
- Performance optimizations for smooth rendering


To implement these styles in your project, simply include the CSS variables and component classes as outlined in the Implementation Guide section.



