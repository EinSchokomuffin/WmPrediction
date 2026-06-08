import { PredictionForm } from "@/components/PredictionForm";
import { getGroups } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  const groups = await getGroups();
  return <PredictionForm groups={groups} />;
}
