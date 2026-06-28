import createIntlMiddleware from "next-intl/middleware";
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

import { routing } from "@/i18n/routing";
import {
  getConfiguredSiteHostnames,
  isBusinessSiteHostname,
} from "@/lib/site-config";

const SESSION_COOKIE = "auth-session";

const protectedPaths = [
  "/leads",
  "/demo-chat",
  "/settings",
  "/getting-started",
];

const intlMiddleware = createIntlMiddleware(routing);

function getPathnameWithoutLocale(pathname: string): string {
  for (const locale of routing.locales) {
    if (locale === routing.defaultLocale) {
      continue;
    }

    if (pathname === `/${locale}`) {
      return "/";
    }

    if (pathname.startsWith(`/${locale}/`)) {
      return pathname.slice(locale.length + 1);
    }
  }

  return pathname;
}

function buildLocalizedPath(pathname: string, locale: string): string {
  if (locale === routing.defaultLocale) {
    return pathname;
  }

  return pathname === "/" ? `/${locale}` : `/${locale}${pathname}`;
}

function resolveLocale(pathname: string): string {
  for (const locale of routing.locales) {
    if (locale === routing.defaultLocale) {
      continue;
    }

    if (pathname === `/${locale}` || pathname.startsWith(`/${locale}/`)) {
      return locale;
    }
  }

  return routing.defaultLocale;
}

function isBusinessSiteAssetPath(pathname: string): boolean {
  return (
    pathname.startsWith("/_next") ||
    pathname.startsWith("/api") ||
    pathname === "/favicon.ico"
  );
}

export default function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  if (pathname.startsWith("/api")) {
    return NextResponse.next();
  }

  const siteHosts = getConfiguredSiteHostnames();
  const onBusinessSite = isBusinessSiteHostname(
    request.headers.get("host"),
    siteHosts,
  );

  if (onBusinessSite) {
    if (isBusinessSiteAssetPath(pathname)) {
      return NextResponse.next();
    }

    if (pathname === "/site" || pathname.startsWith("/site/")) {
      return NextResponse.next();
    }

    const target = request.nextUrl.clone();
    target.pathname = "/site";
    return NextResponse.rewrite(target);
  }

  if (
    siteHosts.length > 0 &&
    (pathname === "/site" || pathname.startsWith("/site/"))
  ) {
    const target = request.nextUrl.clone();
    target.pathname = "/";
    return NextResponse.redirect(target);
  }

  const locale = resolveLocale(pathname);
  const pathnameWithoutLocale = getPathnameWithoutLocale(pathname);
  const hasSession = Boolean(request.cookies.get(SESSION_COOKIE)?.value);
  const isDashboardAlias =
    pathnameWithoutLocale === "/dashboard" ||
    pathnameWithoutLocale.startsWith("/dashboard/");

  if (isDashboardAlias) {
    const target = request.nextUrl.clone();
    target.pathname = buildLocalizedPath("/getting-started", locale);
    target.search = "";
    return NextResponse.redirect(target);
  }

  const isProtected = protectedPaths.some(
    (path) =>
      pathnameWithoutLocale === path ||
      pathnameWithoutLocale.startsWith(`${path}/`),
  );
  const isLogin = pathnameWithoutLocale === "/login";

  if (isProtected && !hasSession) {
    const loginUrl = request.nextUrl.clone();
    loginUrl.pathname = buildLocalizedPath("/login", locale);
    loginUrl.searchParams.set("next", pathnameWithoutLocale);
    return NextResponse.redirect(loginUrl);
  }

  if (isLogin && hasSession) {
    const dashboardUrl = request.nextUrl.clone();
    dashboardUrl.pathname = buildLocalizedPath("/getting-started", locale);
    dashboardUrl.search = "";
    return NextResponse.redirect(dashboardUrl);
  }

  return intlMiddleware(request);
}

export const config = {
  matcher: [
    "/",
    "/site",
    "/site/:path*",
    "/(de|en)/:path*",
    "/dashboard",
    "/dashboard/:path*",
    "/login",
    "/forgot-password",
    "/reset-password",
    "/onboarding",
    "/leads/:path*",
    "/demo-chat/:path*",
    "/settings/:path*",
    "/getting-started/:path*",
  ],
};
