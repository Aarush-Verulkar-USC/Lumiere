import React, { useEffect, useRef } from "react";

interface SquaresProps {
  direction?: "up" | "down" | "left" | "right";
  speed?: number;
  borderColor?: string;
  squareSize?: number;
  hoverFillColor?: string;
}

const Squares: React.FC<SquaresProps> = ({
  direction = "up",
  speed = 0.5,
  borderColor = "#3876BF",
  squareSize = 40,
  hoverFillColor = "#141f44",
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const mouseRef = useRef({ x: 0, y: 0 });
  const squaresRef = useRef<any[]>([]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let animationFrameId: number;

    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      initSquares();
    };

    const initSquares = () => {
      squaresRef.current = [];
      const cols = Math.ceil(canvas.width / squareSize) + 1;
      const rows = Math.ceil(canvas.height / squareSize) + 1;

      for (let i = 0; i < cols; i++) {
        for (let j = 0; j < rows; j++) {
          squaresRef.current.push({
            x: i * squareSize,
            y: j * squareSize,
            opacity: 0,
          });
        }
      }
    };

    const drawSquares = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      squaresRef.current.forEach((square) => {
        const dx = mouseRef.current.x - (square.x + squareSize / 2);
        const dy = mouseRef.current.y - (square.y + squareSize / 2);
        const distance = Math.sqrt(dx * dx + dy * dy);
        const maxDistance = 200;

        // Base opacity for all squares
        let baseOpacity = 0.15;

        if (distance < maxDistance) {
          square.opacity = Math.min(baseOpacity + (1 - distance / maxDistance) * 0.7, 1);
        } else {
          square.opacity = Math.max(square.opacity - 0.03, baseOpacity);
        }

        // Draw base grid
        ctx.strokeStyle = borderColor;
        ctx.globalAlpha = baseOpacity;
        ctx.strokeRect(square.x, square.y, squareSize, squareSize);

        // Draw enhanced hover effect
        if (square.opacity > baseOpacity) {
          ctx.fillStyle = hoverFillColor;
          ctx.globalAlpha = square.opacity - baseOpacity;
          ctx.fillRect(square.x, square.y, squareSize, squareSize);
          ctx.globalAlpha = square.opacity;
          ctx.strokeRect(square.x, square.y, squareSize, squareSize);
        }

        // Movement based on direction
        if (direction === "up") square.y -= speed;
        else if (direction === "down") square.y += speed;
        else if (direction === "left") square.x -= speed;
        else if (direction === "right") square.x += speed;

        // Wrap around
        if (direction === "up" && square.y < -squareSize) {
          square.y = canvas.height;
        } else if (direction === "down" && square.y > canvas.height) {
          square.y = -squareSize;
        } else if (direction === "left" && square.x < -squareSize) {
          square.x = canvas.width;
        } else if (direction === "right" && square.x > canvas.width) {
          square.x = -squareSize;
        }
      });

      ctx.globalAlpha = 1;
    };

    const animate = () => {
      drawSquares();
      animationFrameId = requestAnimationFrame(animate);
    };

    const handleMouseMove = (e: MouseEvent) => {
      mouseRef.current = { x: e.clientX, y: e.clientY };
    };

    const handleMouseLeave = () => {
      mouseRef.current = { x: -9999, y: -9999 };
    };

    resizeCanvas();
    window.addEventListener("resize", resizeCanvas);
    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseleave", handleMouseLeave);

    animate();

    return () => {
      window.removeEventListener("resize", resizeCanvas);
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseleave", handleMouseLeave);
      cancelAnimationFrame(animationFrameId);
    };
  }, [direction, speed, borderColor, squareSize, hoverFillColor]);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none z-0"
      style={{ opacity: 0.8 }}
    />
  );
};

export default Squares;
