import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { ChevronDown } from "lucide-react";

interface ModelSelectProps {
  selectedModel: "gemini" | "nutrix";
  onModelChange: (model: "gemini" | "nutrix") => void;
}

export function ModelSelect({
  selectedModel,
  onModelChange,
}: ModelSelectProps) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" className="w-[120px] justify-between">
          {selectedModel === "gemini" ? "Gemini AI" : "Nutrix AI"}
          <ChevronDown className="ml-2 h-4 w-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent>
        <DropdownMenuItem onClick={() => onModelChange("gemini")}>
          Gemini AI
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => onModelChange("nutrix")}>
          Nutrix AI
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
