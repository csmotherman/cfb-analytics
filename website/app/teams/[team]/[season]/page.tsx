import { redirect } from "next/navigation";
export default async function Page({params}:{params:Promise<{team:string;season:string}>}){const {team,season}=await params;redirect(team.toLowerCase()==="michigan"?`/history/${season}`:"/analytics")}
