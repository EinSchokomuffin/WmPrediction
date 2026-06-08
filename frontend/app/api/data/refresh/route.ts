import { NextResponse } from "next/server";

const BACKEND_BASE = process.env.INTERNAL_API_URL ?? "http://backend:8000";

async function proxyRefresh(method: "GET" | "POST") {
  try {
    const response = await fetch(`${BACKEND_BASE}/api/data/refresh`, {
      method,
      cache: "no-store",
    });

    const payload = await response.json();
    return NextResponse.json(payload, { status: response.status });
  } catch (error) {
    return NextResponse.json(
      {
        status: "error",
        source: "frontend-proxy",
        reason: error instanceof Error ? error.message : "Refresh proxy failed",
        updated_groups: 0,
      },
      { status: 502 },
    );
  }
}

export async function GET() {
  return proxyRefresh("GET");
}

export async function POST() {
  return proxyRefresh("POST");
}