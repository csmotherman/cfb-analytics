import {redirect} from "next/navigation";
export default async function Story({params}:{params:Promise<{slug:string}>}){redirect(`/articles/${(await params).slug}`)}
