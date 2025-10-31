import { ChatKit, useChatKit } from "@openai/chatkit-react";
import type { ColorScheme } from "../hooks/useColorScheme";
import {
  EXAM_PREP_CHATKIT_API_DOMAIN_KEY,
  EXAM_PREP_CHATKIT_API_URL,
  EXAM_PREP_COMPOSER_PLACEHOLDER,
  EXAM_PREP_GREETING,
  EXAM_PREP_STARTER_PROMPTS,
} from "../lib/config";

type ChatKitPanelProps = {
  theme: ColorScheme;
};

export function ChatKitPanel({ theme }: ChatKitPanelProps) {

  const chatkit = useChatKit({
    api: {
      url: EXAM_PREP_CHATKIT_API_URL,
      domainKey: EXAM_PREP_CHATKIT_API_DOMAIN_KEY,
    },
    theme: {
      colorScheme: theme,
      color: {
        grayscale: {
          hue: 225,
          tint: 6,
          shade: theme === "dark" ? -1 : -4,
        },
        accent: {
          primary: theme === "dark" ? "#f1f5f9" : "#0f172a",
          level: 1,
        },
      },
      radius: "round",
    },
    startScreen: {
      greeting: EXAM_PREP_GREETING,
      prompts: EXAM_PREP_STARTER_PROMPTS,
    },
    composer: {
      placeholder: EXAM_PREP_COMPOSER_PLACEHOLDER,
    },
    threadItemActions: {
      feedback: false,
    },
    onError: ({ error }) => {
      // ChatKit propagates the error to the UI; keep logging for debugging.
      console.error("ChatKit error", error);
    },
  });

  return (
    <div className="relative h-full w-full overflow-hidden border border-slate-200/60 bg-white shadow-card dark:border-slate-800/70 dark:bg-slate-900">
      <ChatKit control={chatkit.control} className="block h-full w-full" />
    </div>
  );
}
