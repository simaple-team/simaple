import { useSkillData } from "@/hooks/useSkillData";

interface SkillIconProps {
  name: string;
}

export function SkillIcon(props: SkillIconProps) {
  const { name } = props;

  const { getIconPath } = useSkillData();

  return (
    <div className="inline-flex w-8 h-8">
      <img src={getIconPath(name)} alt={name} className="w-full h-full" />
    </div>
  );
}
