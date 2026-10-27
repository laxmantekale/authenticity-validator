import React from 'react';
import { QRCodeSVG } from 'qrcode.react';

export const QRGenerator = ({ value, size = 200, includeMargin = true }) => {
  if (!value) return null;

  return (
    <div className="inline-flex p-4 bg-white rounded-2xl border border-slate-200 shadow-sm">
      <QRCodeSVG
        value={value}
        size={size}
        level="H"
        includeMargin={includeMargin}
      />
    </div>
  );
};

export default QRGenerator;
