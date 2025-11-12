import { useEffect, useState } from 'react'

interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>
}

export default function InstallAlertBanner() {
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null)
  const [show, setShow] = useState(false)
  const [installed, setInstalled] = useState(false)
  const [showHint, setShowHint] = useState(false)

  const isIOS = typeof navigator !== 'undefined' && /iphone|ipad|ipod/i.test(navigator.userAgent)
  const isStandalone = typeof window !== 'undefined' && (window.matchMedia('(display-mode: standalone)').matches || (navigator as any).standalone === true)

  useEffect(() => {
    if (isStandalone) setInstalled(true)
    const dismissed = typeof window !== 'undefined' ? localStorage.getItem('pwa_install_dismissed') === '1' : false
    if (!dismissed && !isStandalone) setShow(true)

    const onBeforeInstallPrompt = (e: Event) => {
      e.preventDefault()
      setDeferredPrompt(e as BeforeInstallPromptEvent)
      const d = localStorage.getItem('pwa_install_dismissed') === '1'
      if (!d && !isStandalone) setShow(true)
    }

    const onInstalled = () => {
      setInstalled(true)
      setShow(false)
    }

    const mq = window.matchMedia('(display-mode: standalone)')
    const onDMChange = () => {
      if (mq.matches) {
        setInstalled(true)
        setShow(false)
      }
    }

    window.addEventListener('beforeinstallprompt', onBeforeInstallPrompt)
    window.addEventListener('appinstalled', onInstalled)
    if ((mq as any).addEventListener) mq.addEventListener('change', onDMChange)
    else (mq as any).addListener(onDMChange)

    return () => {
      window.removeEventListener('beforeinstallprompt', onBeforeInstallPrompt)
      window.removeEventListener('appinstalled', onInstalled)
      if ((mq as any).removeEventListener) mq.removeEventListener('change', onDMChange)
      else (mq as any).removeListener(onDMChange)
    }
  }, [isStandalone])

  const handleInstall = async () => {
    if (deferredPrompt) {
      await deferredPrompt.prompt()
      const { outcome } = await deferredPrompt.userChoice
      if (outcome === 'accepted') {
        setShow(false)
        setDeferredPrompt(null)
      }
    } else {
      setShowHint(true)
    }
  }

  const handleLater = () => {
    setShow(false)
    localStorage.setItem('pwa_install_dismissed', '1')
  }

  if (!show || installed) return null

  return (
    <div className="fixed bottom-4 left-4 right-4 md:left-auto md:right-4 md:w-96 z-50 animate-slide-up">
      {/* Glassmorphism container */}
      <div className="relative backdrop-blur-xl bg-white/10 dark:bg-black/20 rounded-2xl shadow-2xl border border-white/20 dark:border-white/10 p-5 overflow-hidden">
        {/* Gradient overlay for depth */}
        <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent pointer-events-none"></div>
        
        {/* Content */}
        <div className="relative flex items-start gap-4">
          {/* Icon with glass effect */}
          <div className="flex-shrink-0 p-2 rounded-xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 backdrop-blur-sm border border-white/20">
            <svg className="w-8 h-8 text-blue-400 drop-shadow-lg" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
            </svg>
          </div>
          
          <div className="flex-1">
            <h3 className="font-bold text-white text-lg mb-1 drop-shadow-md">تثبيت التطبيق</h3>
            <p className="text-sm text-white/90 mb-3 drop-shadow">ثبت تطبيق Ornina للوصول السريع والاستخدام دون اتصال</p>
            
            {showHint && (
              <div className="text-xs text-white/80 mb-3 p-2 rounded-lg bg-white/10 backdrop-blur-sm border border-white/20">
                {isIOS ? (
                  <p>افتح مشاركة ثم "إضافة إلى الشاشة الرئيسية" في Safari</p>
                ) : (
                  <p>استخدم زر التثبيت في شريط العنوان أو قائمة المتصفح</p>
                )}
              </div>
            )}
            
            <div className="flex gap-2">
              <button 
                onClick={handleInstall} 
                className="flex-1 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white px-4 py-2.5 rounded-xl text-sm font-semibold transition-all duration-300 shadow-lg hover:shadow-xl hover:scale-105 backdrop-blur-sm"
              >
                تثبيت
              </button>
              <button 
                onClick={handleLater} 
                className="px-4 py-2.5 text-white/90 hover:text-white bg-white/10 hover:bg-white/20 backdrop-blur-sm rounded-xl text-sm font-medium transition-all duration-300 border border-white/20 hover:border-white/30"
              >
                لاحقاً
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
