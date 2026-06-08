import { GroupSetupEditor } from "@/components/GroupSetupEditor";
import { getGroups } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function SetupPage() {
  const groups = await getGroups();

  return <GroupSetupEditor initialGroups={groups} />;
}