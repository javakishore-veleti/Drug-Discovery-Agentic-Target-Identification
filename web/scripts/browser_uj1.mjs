#!/usr/bin/env node
/**
 * Headless browser smoke for UJ-1 (Stories 5.1–5.4):
 * sign-in → Disclaimer → mechanism → cardiotoxicity follow-up → sign-out.
 */
import { chromium } from "playwright";

const BASE = process.env.WEB_URL || "http://127.0.0.1:5173";
const EMAIL = process.env.SMOKE_USER_EMAIL || "asha.demo@example.com";
const PASSWORD = process.env.SMOKE_USER_PASSWORD || "ChangeMe-Demo12";

async function main() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  page.setDefaultTimeout(320_000);

  await page.goto(BASE);
  await page.getByLabel("Email").fill(EMAIL);
  await page.getByLabel("Password").fill(PASSWORD);
  await page.getByRole("button", { name: "Sign in" }).click();

  await page.getByRole("note", { name: "Research disclaimer" }).waitFor();
  const disclaimer = await page.getByRole("note").innerText();
  if (!/Research assistance only/i.test(disclaimer)) {
    throw new Error("Disclaimer missing approved copy");
  }

  await page.getByRole("button", { name: "Demo: mechanism" }).click();
  await page.getByText("tool_use:", { exact: false }).first().waitFor({ timeout: 300_000 });
  await page.getByText("Streaming…").waitFor({ state: "detached", timeout: 300_000 }).catch(() => {});
  // Wait for done turn (Streaming… gone or answer present)
  await page.waitForFunction(
    () => {
      const tools = document.body.innerText.includes("tool_use:");
      const answer = document.querySelector(".answer");
      const streaming = document.body.innerText.includes("Streaming…");
      return tools && answer && answer.textContent && answer.textContent.length > 40 && !streaming;
    },
    { timeout: 300_000 },
  );

  await page.getByRole("button", { name: "Demo: cardiotoxicity" }).click();
  await page.waitForFunction(
    () => {
      const answers = [...document.querySelectorAll(".answer")];
      if (answers.length < 2) return false;
      const last = answers[answers.length - 1]?.textContent || "";
      return /herceptin|trastuzumab|her2|erbb2/i.test(last);
    },
    { timeout: 300_000 },
  );

  await page.getByRole("button", { name: "Sign out" }).click();
  await page.getByRole("button", { name: "Sign in" }).waitFor();

  console.log(JSON.stringify({ ok: true, uj1: true, url: BASE }, null, 2));
  await browser.close();
}

main().catch(async (err) => {
  console.error(err);
  process.exit(1);
});
