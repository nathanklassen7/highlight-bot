import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ToastProvider } from "./components/shared/Toast";
import { HomePage } from "./pages/HomePage";
import { ClipsPage } from "./pages/ClipsPage";
import { ViewClipPage } from "./pages/ViewClipPage";
import { ConfigPage } from "./pages/ConfigPage";
import { WifiPage } from "./pages/WifiPage";

export function App() {
  return (
    <BrowserRouter>
      <ToastProvider>
        <div className="bg-gray-100 min-h-screen">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/clips" element={<ClipsPage />} />
            <Route path="/clips/view/*" element={<ViewClipPage />} />
            <Route path="/config" element={<ConfigPage />} />
            <Route path="/wifi" element={<WifiPage />} />
          </Routes>
        </div>
      </ToastProvider>
    </BrowserRouter>
  );
}
