import { notFound } from "next/navigation";
import { use } from "react";
import { getCatalog, getCollections } from "../../actions";
import CatalogPage from "../../components/pages/catalog";
import Root from "../../stac/catalog.json";
import type { Catalog } from "../../types/Stac";

type Params = { id: string };

export default function Page({ params }) {
  const { id } = use(params) as Params;
  const link = Root["links"].find(link => link["heystac:id"] == id);
  if (!link) {
    notFound();
  }
  const catalog = getCatalog(id);
  const collections = getCollections(catalog);
  return (
    <CatalogPage
      catalog={catalog}
      collections={collections}
      title={link.title}
    ></CatalogPage>
  );
}

export async function generateStaticParams() {
  const stac_catalog: Catalog = Root;
  return stac_catalog.links.map(link => ({
    id: link["heystac:id"],
  }));
}
