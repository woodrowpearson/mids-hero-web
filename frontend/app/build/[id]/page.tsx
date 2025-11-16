/**
 * Build Viewer Page - Shared build display
 * Epic 1.3: Layout Shell + Navigation
 *
 * SSR page for viewing shared builds with rich preview metadata
 */

import { Metadata } from "next";
import { BuildLayout } from "@/components/layout/BuildLayout";

export async function generateMetadata({
  params,
}: {
  params: { id: string };
}): Promise<Metadata> {
  // TODO: Fetch build from backend (Epic 6)
  // For now, return default metadata
  return {
    title: `Shared Build - Mids Hero Web`,
    description: `View a shared City of Heroes build`,
    openGraph: {
      title: `Shared Build`,
      description: `A City of Heroes character build`,
      type: "website",
    },
    twitter: {
      card: "summary_large_image",
      title: `Shared Build`,
      description: `A City of Heroes character build`,
    },
  };
}

export default async function BuildViewerPage({
  params,
}: {
  params: { id: string };
}) {
  // TODO: Fetch build from backend (Epic 6)
  // For now, show placeholder

  return (
    <BuildLayout columnCount={3} showSidebar={false}>
      <div className="col-span-full p-12 text-center space-y-4">
        <h2 className="text-2xl font-semibold">Shared Build</h2>
        <p className="text-muted-foreground">Build ID: {params.id}</p>
        <p className="text-sm text-muted-foreground/75 max-w-md mx-auto">
          Build loading will be implemented in Epic 6 (Build Persistence).
          This page will display shared builds with rich preview cards for
          Discord and Twitter.
        </p>
      </div>
    </BuildLayout>
  );
}
