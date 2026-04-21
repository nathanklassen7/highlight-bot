import { Header } from "../components/layout/Header";
import { PageLayout } from "../components/layout/PageLayout";
import { StatusIndicator } from "../components/home/StatusIndicator";
import { BotControls } from "../components/home/BotControls";
import { NavLinks } from "../components/home/NavLinks";
import { useBotStatus } from "../hooks/useBotStatus";

export function HomePage() {
  const { state, refresh } = useBotStatus();

  return (
    <>
      <Header title="Highlight Bot" />
      <PageLayout>
        <div className="space-y-6">
          <StatusIndicator state={state} />
          <BotControls state={state} onAction={refresh} />
          <NavLinks />
        </div>
      </PageLayout>
    </>
  );
}
