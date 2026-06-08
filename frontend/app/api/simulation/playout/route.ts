import { NextResponse } from "next/server";

const BACKEND_BASE = process.env.INTERNAL_API_URL ?? "http://backend:8000";

export async function POST() {
  try {
    const response = await fetch(`${BACKEND_BASE}/api/simulation/playout`, {
      method: "POST",
      cache: "no-store",
    });

    const payload = await response.json();
    return NextResponse.json(payload, { status: response.status });
  } catch (error) {
    return NextResponse.json(
      {
        status: "error",
        reason: error instanceof Error ? error.message : "Tournament playout proxy failed",
      },
      { status: 502 },
    );
  }
}