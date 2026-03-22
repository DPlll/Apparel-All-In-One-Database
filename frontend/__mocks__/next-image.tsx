import React from "react";
const Image = ({ src, alt, ...props }: { src: string; alt: string; [key: string]: unknown }) => {
  return React.createElement("img", { src, alt, ...props });
};
export default Image;
