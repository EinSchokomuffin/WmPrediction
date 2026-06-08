import { BracketList } from "@/components/tournament/BracketList";
import { getBracket } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function BracketPage() {
  const bracket = await getBracket().catch(() => ({ round_of_32: [] }));

  return (
    <section>
      <BracketList matches={bracket.round_of_32} />
    </section>
  );
}
