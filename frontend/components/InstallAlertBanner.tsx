import { useEffect, useState } from 'react'
import { DevicePhoneMobileIcon, ComputerDesktopIcon, ShareIcon, PlusCircleIcon } from '@heroicons/react/24/outline'

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
    // If already showing hint, toggle it off
    if (showHint) {
      setShowHint(false)
      return
    }

    if (deferredPrompt) {
      try {
        await deferredPrompt.prompt()
        const { outcome } = await deferredPrompt.userChoice
        if (outcome === 'accepted') {
          setShow(false)
          setDeferredPrompt(null)
        }
      } catch (error) {
        console.error('Error showing install prompt:', error)
        setShowHint(true)
      }
    } else {
      // No deferred prompt available - show browser-specific instructions
      setShowHint(true)
    }
  }

  const handleLater = () => {
    setShow(false)
    localStorage.setItem('pwa_install_dismissed', '1')
  }

  if (!show || installed) return null

  return (
    <div className="fixed bottom-4 left-4 right-4 md:left-auto md:right-4 md:max-w-sm z-50 animate-slide-up">
      {/* Glassmorphism container */}
      <div className="relative backdrop-blur-xl bg-white/10 dark:bg-black/20 rounded-xl shadow-2xl border border-white/20 dark:border-white/10 p-3 overflow-hidden">
        {/* Gradient overlay for depth */}
        <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent pointer-events-none"></div>

        {/* Content */}
        <div className="relative flex items-start gap-3">
          {/* Icon with glass effect */}
          <div className="flex-shrink-0 p-1.5 rounded-lg bg-white/10 backdrop-blur-sm border border-white/20">
            <DevicePhoneMobileIcon className="w-6 h-6 text-white/90 drop-shadow-lg" />
          </div>

          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-white text-sm mb-0.5 drop-shadow-md">تثبيت التطبيق</h3>
            <p className="text-xs text-white/80 mb-2 drop-shadow">ثبت Ornina للوصول السريع</p>

            {showHint && (
              <div className="text-[10px] text-white/80 mb-2 p-2 rounded-lg bg-white/10 backdrop-blur-sm border border-white/20">
                {isIOS ? (
                  <>
                    <div className="flex items-center gap-1 mb-1">
                      <DevicePhoneMobileIcon className="w-3 h-3 text-white/70" />
                      <p className="font-semibold text-[11px]">iOS:</p>
                    </div>
                    <ol className="list-decimal list-inside space-y-0.5 text-white/70 mr-3 text-[10px]">
                      <li className="flex items-center gap-1">
                        <span>اضغط على زر المشاركة</span>
                        <ShareIcon className="w-3 h-3 inline-block" />
                      </li>
                      <li className="flex items-center gap-1">
                        <span>اختر "إضافة للشاشة الرئيسية"</span>
                        <PlusCircleIcon className="w-3 h-3 inline-block" />
                      </li>
                    </ol>
                  </>
                ) : (
                  <>
                    <div className="flex items-center gap-1 mb-1">
                      <ComputerDesktopIcon className="w-3 h-3 text-white/70" />
                      <p className="font-semibold text-[11px]">التثبيت:</p>
                    </div>
                    <ul className="space-y-0.5 text-white/70 mr-2 text-[10px]">
                      <li>• ابحث عن أيقونة التثبيت بشريط العنوان</li>
                      <li>• أو القائمة ← "تثبيت التطبيق"</li>
                    </ul>
                  </>
                )}
              </div>
            )}

            <div className="flex gap-1.5">
              <button
                onClick={handleInstall}
                className="flex-1 bg-white/10 hover:bg-white/20 text-white px-3 py-1.5 rounded-lg text-xs font-semibold transition-all duration-300 shadow-lg hover:shadow-xl hover:scale-105 backdrop-blur-sm border border-white/20"
              >
                {showHint ? 'إخفاء' : deferredPrompt ? 'تثبيت' : 'التعليمات'}
              </button>
              <button
                onClick={handleLater}
                className="px-3 py-1.5 text-white/90 hover:text-white bg-white/10 hover:bg-white/20 backdrop-blur-sm rounded-lg text-xs font-medium transition-all duration-300 border border-white/20 hover:border-white/30"
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
