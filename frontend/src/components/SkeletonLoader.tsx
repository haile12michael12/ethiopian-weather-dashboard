import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

export function CurrentWeatherSkeleton() {
  return (
    <Card className="p-6 md:p-8 border border-card-border col-span-1 md:col-span-2">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div className="flex-1 space-y-4">
          <Skeleton className="h-8 w-48" />
          <Skeleton className="h-4 w-64" />
          <div className="space-y-2 mt-6">
            <Skeleton className="h-20 w-40" />
            <Skeleton className="h-6 w-32" />
          </div>
        </div>
        <Skeleton className="h-24 w-24 rounded-full" />
      </div>
    </Card>
  );
}

export function StatsGridSkeleton() {
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-2 xl:grid-cols-3 gap-4">
      {Array.from({ length: 5 }).map((_, i) => (
        <Card key={i} className="p-4 border border-card-border">
          <div className="flex items-start justify-between gap-3">
            <div className="flex-1 space-y-2">
              <Skeleton className="h-3 w-16" />
              <Skeleton className="h-6 w-20" />
            </div>
            <Skeleton className="h-10 w-10 rounded-md" />
          </div>
        </Card>
      ))}
    </div>
  );
}

export function WeatherChartSkeleton() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6">
      {Array.from({ length: 2 }).map((_, i) => (
        <Card key={i} className="p-4 md:p-6 border border-card-border">
          <Skeleton className="h-6 w-40 mb-4" />
          <Skeleton className="h-64 w-full" />
        </Card>
      ))}
    </div>
  );
}
