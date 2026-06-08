import { NextRequest, NextResponse } from "next/server";

const BACKEND_BASE = process.env.INTERNAL_API_URL ?? "http://backend:8000";

export async function GET(request: NextRequest) {
  try {
    const home = request.nextUrl.searchParams.get("home") ?? "";
    const away = request.nextUrl.searchParams.get("away") ?? "";
    const query = new URLSearchParams({ home, away }).toString();

    const response = await fetch(`${BACKEND_BASE}/api/predictions/match?${query}`, {
      method: "GET",
      cache: "no-store",
    });

    const payload = await response.json();
    return NextResponse.json(payload, { status: response.status });
  } catch (error) {
    return NextResponse.json(
      { detail: error instanceof Error ? error.message : "Prediction proxy failed" },
      { status: 502 },
    );
  }
}