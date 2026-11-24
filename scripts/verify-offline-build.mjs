// Copyright © 2026 Christopher Snow. Verify what Actions actually downloaded.
import { readFile } from "node:fs/promises";
import { createHash } from "node:crypto";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { validateRelease } from "../src/release-contract.mjs";
export async function verifyOfflineBuild(directory) {
  const release = validateRelease(
    JSON.parse(await readFile(directory + "/release.json", "utf8")),
  );
  const pinned = validateRelease(
    JSON.parse(
      await readFile(
        directory + "/releases/" + release.id + "/release.json",
        "utf8",
      ),
    ),
  );
  if (
    pinned.id !== release.id ||
    pinned.bytes !== release.bytes ||
    JSON.stringify(pinned.files) !== JSON.stringify(release.files)
  )
    throw Error("Publication manifests disagree.");
  for (const file of release.files) {
    let bytes;
    try {
      bytes = await readFile(
        directory + "/releases/" + release.id + "/" + file.path,
      );
    } catch {
      throw Error("Publication artifact is missing " + file.path);
    }
    if (
      bytes.length !== file.bytes ||
      createHash("sha256").update(bytes).digest("hex") !== file.sha256
    )
      throw Error("Publication artifact failed verification: " + file.path);
  }
  return release;
}
if (
  process.argv[1] &&
  resolve(process.argv[1]) === fileURLToPath(import.meta.url)
) {
  const release = await verifyOfflineBuild(process.argv[2] || "dist");
  console.log(
    "Verified publication artifact:",
    release.files.length,
    "files,",
    release.bytes,
    "bytes.",
  );
}
