import {
  createContext,
  useContext,
  useState,
  useCallback,
  useRef,
  type ReactNode,
} from "react";

interface ToastContextType {
  showSuccess: (msg: string) => void;
  showError: (msg: string) => void;
}

const ToastContext = createContext<ToastContextType>({
  showSuccess: () => {},
  showError: () => {},
});

export function useToast() {
  return useContext(ToastContext);
}

export function ToastProvider({ children }: { children: ReactNode }) {
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);
  const [visible, setVisible] = useState(false);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const show = useCallback((msg: string, error: boolean) => {
    if (timerRef.current != null) clearTimeout(timerRef.current);
    setMessage(msg);
    setIsError(error);
    setVisible(true);
    timerRef.current = setTimeout(() => setVisible(false), 3000);
  }, []);

  const showSuccess = useCallback((msg: string) => show(msg, false), [show]);
  const showError = useCallback((msg: string) => show(msg, true), [show]);

  return (
    <ToastContext.Provider value={{ showSuccess, showError }}>
      {children}
      <div
        className={`fixed top-3 left-1/2 -translate-x-1/2 px-5 py-2 rounded-lg text-sm font-medium z-50 transition-opacity duration-300 pointer-events-none ${
          visible ? "opacity-100" : "opacity-0"
        }`}
        style={{
          background: isError ? "#fee2e2" : "#dcfce7",
          color: isError ? "#b91c1c" : "#15803d",
        }}
      >
        {message}
      </div>
    </ToastContext.Provider>
  );
}
