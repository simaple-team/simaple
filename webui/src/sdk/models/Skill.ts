export interface Skill {
  kind: "Component";
  data: Record<string, any>;
  metadata: SkillMetadata;
  patch: string[];
  version: string;
}

export interface SkillMetadata {
  annotation: Record<string, any>;
  label: {
    group: string;
    id: string;
    name: string;
  };
}
