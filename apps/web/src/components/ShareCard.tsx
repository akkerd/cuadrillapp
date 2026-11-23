import { Copy, QrCode, Share2 } from "lucide-react";
import { useEffect, useState } from "react";
import { copy } from "../copy";
import { roomLink } from "../lib/format";
import { useStore } from "../store";
import { Button, Card } from "./ui";

export function ShareCard({ code }: { code: string }) {
  const [qr, setQr] = useState<string | null>(null);
  const [showQr, setShowQr] = useState(false);
  const link = roomLink(code);
  const toast = useStore((s) => s.toast);

  useEffect(() => {
    if (!showQr || qr) return;
    void import("qrcode")
      .then((QRCode) =>
        QRCode.toDataURL(link, {
          margin: 1,
          width: 480,
          color: { dark: "#1E1338", light: "#FFF9EE" },
        }),
      )
      .then(setQr);
  }, [showQr, qr, link]);

  return (
    <Card className="rotate-[0.6deg]">
      <p className="text-center text-5xl font-bold tracking-[0.25em] text-ink">
        <span className="sr-only">Código: </span>
        {code}
      </p>
      <div className="mt-4 grid grid-cols-3 gap-2">
        <Button
          size="sm"
          tone="sun"
          icon={Copy}
          onClick={async () => {
            try {
              await navigator.clipboard.writeText(link);
              toast(copy.copied);
            } catch {
              toast(link);
            }
          }}
        >
          {copy.copy}
        </Button>
        <Button
          size="sm"
          tone="mint"
          icon={QrCode}
          aria-pressed={showQr}
          onClick={() => setShowQr((v) => !v)}
        >
          {copy.qr}
        </Button>
        <Button
          size="sm"
          tone="pink"
          icon={Share2}
          disabled={typeof navigator.share !== "function"}
          onClick={() =>
            void navigator
              .share?.({ title: copy.app, text: copy.shareText, url: link })
              .catch(() => {})
          }
        >
          {copy.share}
        </Button>
      </div>
      {showQr && qr && (
        <img
          src={qr}
          alt={`QR ${code}`}
          className="mx-auto mt-4 w-56 rounded-2xl border-[3px] border-ink"
        />
      )}
    </Card>
  );
}
