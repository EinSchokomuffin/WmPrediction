import { NextRequest, NextResponse } from "next/server";

const BACKEND_BASE = process.env.INTERNAL_API_URL ?? "http://backend:8000";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const response = await fetch(`${BACKEND_BASE}/api/groups/setup-all`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      cache: "no-store",
    });

    const payload = await response.json();
    return NextResponse.json(payload, { status: response.status });
  } catch (error) {
    return NextResponse.json(
      {
        status: "error",
        reason: error instanceof Error ? error.message : "Group setup proxy failed",
      },
      { status: 502 },
    );
  }
}