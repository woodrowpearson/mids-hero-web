/**
 * API client tests
 */

import { describe, it, expect } from "vitest";
import api from "@/services/api";
import { archetypeApi } from "@/services/archetypeApi";
import { powerApi } from "@/services/powerApi";

describe("API Client", () => {
  it("exports api instance", () => {
    expect(api).toBeDefined();
  });

  it("has defaults configured", () => {
    expect(api.defaults).toBeDefined();
  });
});

describe("Archetype API", () => {
  it("exports getAll method", () => {
    expect(archetypeApi.getAll).toBeDefined();
    expect(typeof archetypeApi.getAll).toBe("function");
  });

  it("exports getById method", () => {
    expect(archetypeApi.getById).toBeDefined();
    expect(typeof archetypeApi.getById).toBe("function");
  });
});

describe("Power API", () => {
  it("exports getPowersets method", () => {
    expect(powerApi.getPowersets).toBeDefined();
    expect(typeof powerApi.getPowersets).toBe("function");
  });

  it("exports getPowersetPowers method", () => {
    expect(powerApi.getPowersetPowers).toBeDefined();
    expect(typeof powerApi.getPowersetPowers).toBe("function");
  });

  it("exports getAllPowers method", () => {
    expect(powerApi.getAllPowers).toBeDefined();
    expect(typeof powerApi.getAllPowers).toBe("function");
  });

  it("exports getPowerById method", () => {
    expect(powerApi.getPowerById).toBeDefined();
    expect(typeof powerApi.getPowerById).toBe("function");
  });
});
