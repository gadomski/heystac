import Link from "next/link";
import { Heading, Subtitle } from "../typography";
import { use } from "react";
import { CollecticonExpandTopRight } from "@devseed-ui/collecticons-react";
import Map from "../map";

export default function CatalogPage({ title, href }) {
  const data = use(fetch(href));
  const catalog = use(data.json());

  return (
    <div className="px-8 py-4 grid grid-cols-1 md:grid-cols-[320px,1fr] md:grid-rows-[auto,1fr] grid-rows-[auto,1fr,1fr] gap-4 h-full">
      <div className="row-span-1 col-span-2">
        <Heading>
          <div className="flex items-center">
            {title}
            <span className="mx-2">
              <Link href={href}>
                <CollecticonExpandTopRight />
              </Link>
            </span>
          </div>
        </Heading>
        <Subtitle>STAC version {catalog["stac_version"]}</Subtitle>
      </div>

      <div className="row-start-2 col-start-1 border border-gray-200 p-4">
        Placeholder for your content
      </div>

      <div className="row-start-3 col-start-1 md:col-start-2 md:row-start-2">
        <Map center={[-105, 39.7373]} zoom={2} />
      </div>
    </div>
  );
}
