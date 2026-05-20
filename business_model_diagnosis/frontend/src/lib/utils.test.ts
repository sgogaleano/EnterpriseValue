import { describe, expect, it } from "vitest"
import { cn } from "./utils"

describe("cn", () => {
  it("merges classes", () => {
    expect(cn("p-2", "text-sm", "p-4")).toBe("text-sm p-4")
  })
})
