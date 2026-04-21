import { useEffect, useState } from "react";
import { Header } from "../components/layout/Header";
import { PageLayout } from "../components/layout/PageLayout";
import { WifiStatusDisplay } from "../components/wifi/WifiStatus";
import { ConnectForm } from "../components/wifi/ConnectForm";
import { getWifiStatus } from "../api/wifi";
import type { WifiStatus } from "../types";

export function WifiPage() {
  const [status, setStatus] = useState<WifiStatus | null>(null);

  useEffect(() => {
    getWifiStatus()
      .then(setStatus)
      .catch(() => {});
  }, []);

  return (
    <>
      <Header
        title="WiFi Settings"
        backTo={{ label: "Back", path: "/" }}
      />
      <PageLayout>
        <WifiStatusDisplay status={status} />
        <ConnectForm />
      </PageLayout>
    </>
  );
}
