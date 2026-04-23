/**
 * Telegram WebApp Hook
 * =====================
 * Detects when the app is running as a Telegram Mini App
 * and exposes the WebApp API for native Telegram integration.
 */
import { useState, useEffect } from 'react';

interface TelegramUser {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  language_code?: string;
  is_premium?: boolean;
}

interface TelegramWebApp {
  initData: string;
  initDataUnsafe: {
    user?: TelegramUser;
    query_id?: string;
    auth_date?: number;
    hash?: string;
  };
  version: string;
  platform: string;
  colorScheme: 'light' | 'dark';
  themeParams: Record<string, string>;
  isExpanded: boolean;
  viewportHeight: number;
  viewportStableHeight: number;
  headerColor: string;
  backgroundColor: string;
  setHeaderColor: (color: string) => void;
  setBackgroundColor: (color: string) => void;
  ready: () => void;
  expand: () => void;
  close: () => void;
  enableClosingConfirmation: () => void;
  disableClosingConfirmation: () => void;
  onEvent: (event: string, callback: (...args: any[]) => void) => void;
  offEvent: (event: string, callback: (...args: any[]) => void) => void;
  sendData: (data: string) => void;
  switchInlineQuery: (query: string, choose_chat_types?: string[]) => void;
  openLink: (url: string, options?: { try_instant_view?: boolean }) => void;
  openTelegramLink: (url: string) => void;
  openInvoice: (url: string, callback?: (status: string) => void) => void;
  showPopup: (params: any, callback?: (id?: string) => void) => void;
  showAlert: (message: string, callback?: () => void) => void;
  showConfirm: (message: string, callback?: (confirmed: boolean) => void) => void;
  showScanQrPopup: (params: any, callback?: (text: string) => boolean | void) => void;
  closeScanQrPopup: () => void;
  readTextFromClipboard: (callback?: (text: string) => void) => void;
  requestWriteAccess: (callback?: (access: boolean) => void) => void;
  requestContact: (callback?: (contact: any) => void) => void;
  invokeCustomMethod: (method: string, params: any, callback?: (result: any) => void) => void;
  HapticFeedback: {
    impactOccurred: (style: string) => void;
    notificationOccurred: (type: string) => void;
    selectionChanged: () => void;
  };
  MainButton: {
    text: string;
    color: string;
    textColor: string;
    isVisible: boolean;
    isActive: boolean;
    isProgressVisible: boolean;
    setText: (text: string) => void;
    onClick: (callback: () => void) => void;
    offClick: (callback: () => void) => void;
    show: () => void;
    hide: () => void;
    enable: () => void;
    disable: () => void;
    showProgress: (leaveActive: boolean) => void;
    hideProgress: () => void;
    setParams: (params: any) => void;
  };
  BackButton: {
    isVisible: boolean;
    onClick: (callback: () => void) => void;
    offClick: (callback: () => void) => void;
    show: () => void;
    hide: () => void;
  };
  SettingsButton: {
    isVisible: boolean;
    onClick: (callback: () => void) => void;
    offClick: (callback: () => void) => void;
    show: () => void;
    hide: () => void;
  };
}

declare global {
  interface Window {
    Telegram?: {
      WebApp: TelegramWebApp;
    };
  }
}

export function useTelegramWebApp() {
  const [isReady, setIsReady] = useState(false);
  const [isInTelegram, setIsInTelegram] = useState(false);
  const [telegramUser, setTelegramUser] = useState<TelegramUser | null>(null);
  const [webApp, setWebApp] = useState<TelegramWebApp | null>(null);

  useEffect(() => {
    const twa = window.Telegram?.WebApp;
    if (!twa) {
      setIsInTelegram(false);
      setIsReady(true);
      return;
    }

    setIsInTelegram(true);
    setWebApp(twa);

    // Read user from initDataUnsafe
    const user = twa.initDataUnsafe?.user;
    if (user) {
      setTelegramUser(user);
    }

    // Tell Telegram the app is ready
    twa.ready();

    // Expand to full height
    twa.expand();

    // Set header color to match our dark theme
    try {
      twa.setHeaderColor('#0a0a0f');
      twa.setBackgroundColor('#0a0a0f');
    } catch {
      // Methods may not be available in older WebApp versions
    }

    setIsReady(true);
  }, []);

  return {
    isReady,
    isInTelegram,
    telegramUser,
    webApp,
    // Helpers
    showAlert: (message: string) => webApp?.showAlert(message),
    showConfirm: (message: string, callback: (confirmed: boolean) => void) => webApp?.showConfirm(message, callback),
    hapticFeedback: webApp?.HapticFeedback,
    mainButton: webApp?.MainButton,
    backButton: webApp?.BackButton,
    sendData: (data: string) => webApp?.sendData(data),
    openInvoice: (url: string, callback?: (status: string) => void) => webApp?.openInvoice(url, callback),
  };
}
