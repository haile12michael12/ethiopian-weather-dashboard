import React, { useState } from "react";
import {
  ComposedChart,
  Line,
  Bar,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import { motion } from "framer-motion";
import { COLORS } from "../theme";

/**
 * Advanced chart component with multiple visualization options
 */
const AdvancedForecastChart = ({ city, compareCities = [], unit = "C" }) => {
  const [chartType, setChartType] = useState("composed");
  const [activeMetrics, setActiveMetrics] = useState({
    max: true,
    min: true,
    rain: true,
  });

  if (!city || !city.days || city.days.length === 0) {
    return <div>No forecast data available</div>;
  }

  const chartVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.5, ease: "easeOut" },
    },
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.2,
      },
    },
  };

  const toggleMetric = (metric) => {
    setActiveMetrics((prev) => ({
      ...prev,
      [metric]: !prev[metric],
    }));
  };

  const data = city.days.map((day, idx) => {
    const date = new Date(day.date);
    const dayName = date.toLocaleDateString("en-US", { weekday: "short" });
    return {
      date: dayName,
      fullDate: date.toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
      }),
      max: day.max,
      min: day.min,
      rain: day.rain_percent || 0,
      wind: day.wind || 0,
    };
  });

  const renderChart = () => {
    switch (chartType) {
      case "area":
        return (
          <ResponsiveContainer width="100%" height={300}>
            <ComposedChart data={data}>
              <defs>
                <linearGradient id="colorMax" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ff6b6b" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#ff6b6b" stopOpacity={0.1} />
                </linearGradient>
                <linearGradient id="colorMin" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#4ecdc4" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#4ecdc4" stopOpacity={0.1} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis yAxisId="left" />
              {activeMetrics.max && (
                <Area
                  yAxisId="left"
                  type="monotone"
                  dataKey="max"
                  fill="url(#colorMax)"
                  stroke="#ff6b6b"
                  name="Max Temp"
                  isAnimationActive={true}
                  animationDuration={800}
                />
              )}
              {activeMetrics.min && (
                <Area
                  yAxisId="left"
                  type="monotone"
                  dataKey="min"
                  fill="url(#colorMin)"
                  stroke="#4ecdc4"
                  name="Min Temp"
                  isAnimationActive={true}
                  animationDuration={800}
                />
              )}
              <Tooltip
                contentStyle={{
                  backgroundColor: COLORS.cardBg,
                  border: `1px solid ${COLORS.border}`,
                  borderRadius: 8,
                }}
                labelFormatter={(value) => `Day: ${value}`}
              />
              <Legend />
            </ComposedChart>
          </ResponsiveContainer>
        );

      case "bar":
        return (
          <ResponsiveContainer width="100%" height={300}>
            <ComposedChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis yAxisId="left" />
              <YAxis yAxisId="right" orientation="right" />
              {activeMetrics.max && (
                <Bar
                  yAxisId="left"
                  dataKey="max"
                  fill="#ff6b6b"
                  name="Max Temp"
                  isAnimationActive={true}
                  animationDuration={800}
                  radius={[8, 8, 0, 0]}
                />
              )}
              {activeMetrics.rain && (
                <Bar
                  yAxisId="right"
                  dataKey="rain"
                  fill="#45b7d1"
                  name="Rain %"
                  isAnimationActive={true}
                  animationDuration={800}
                  radius={[8, 8, 0, 0]}
                  opacity={0.6}
                />
              )}
              <Tooltip
                contentStyle={{
                  backgroundColor: COLORS.cardBg,
                  border: `1px solid ${COLORS.border}`,
                  borderRadius: 8,
                }}
              />
              <Legend />
            </ComposedChart>
          </ResponsiveContainer>
        );

      default: // composed
        return (
          <ResponsiveContainer width="100%" height={300}>
            <ComposedChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis yAxisId="left" />
              <YAxis yAxisId="right" orientation="right" />
              <ReferenceLine yAxisId="left" y={20} stroke="#ccc" strokeDasharray="3 3" />
              {activeMetrics.max && (
                <Line
                  yAxisId="left"
                  type="monotone"
                  dataKey="max"
                  stroke="#ff6b6b"
                  strokeWidth={2}
                  dot={{ r: 4 }}
                  activeDot={{ r: 6 }}
                  name="Max Temp"
                  isAnimationActive={true}
                  animationDuration={800}
                />
              )}
              {activeMetrics.min && (
                <Line
                  yAxisId="left"
                  type="monotone"
                  dataKey="min"
                  stroke="#4ecdc4"
                  strokeWidth={2}
                  dot={{ r: 4 }}
                  activeDot={{ r: 6 }}
                  name="Min Temp"
                  isAnimationActive={true}
                  animationDuration={800}
                />
              )}
              {activeMetrics.rain && (
                <Bar
                  yAxisId="right"
                  dataKey="rain"
                  fill="#45b7d1"
                  name="Rain %"
                  isAnimationActive={true}
                  animationDuration={800}
                  opacity={0.5}
                />
              )}
              <Tooltip
                contentStyle={{
                  backgroundColor: COLORS.cardBg,
                  border: `1px solid ${COLORS.border}`,
                  borderRadius: 8,
                }}
                formatter={(value, name) => [
                  typeof value === "number" ? value.toFixed(1) : value,
                  name,
                ]}
              />
              <Legend />
            </ComposedChart>
          </ResponsiveContainer>
        );
    }
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      style={{
        backgroundColor: COLORS.cardBg,
        borderRadius: 12,
        padding: 20,
        marginBottom: 24,
        border: `1px solid ${COLORS.border}`,
      }}
    >
      <motion.div variants={chartVariants} style={{ marginBottom: 16 }}>
        <h3 style={{ margin: "0 0 12px 0", color: COLORS.text }}>
          {city.name} - 7-Day Forecast
        </h3>
        <p style={{ margin: 0, fontSize: 12, color: COLORS.textMuted }}>
          Interactive weather visualization with multiple chart types
        </p>
      </motion.div>

      <motion.div
        variants={chartVariants}
        style={{
          display: "flex",
          gap: 8,
          marginBottom: 16,
          flexWrap: "wrap",
        }}
      >
        <select
          value={chartType}
          onChange={(e) => setChartType(e.target.value)}
          style={{
            padding: "8px 12px",
            borderRadius: 6,
            border: `1px solid ${COLORS.border}`,
            backgroundColor: COLORS.cardBg,
            color: COLORS.text,
            cursor: "pointer",
            fontSize: 12,
          }}
        >
          <option value="composed">Composed Chart</option>
          <option value="area">Area Chart</option>
          <option value="bar">Bar Chart</option>
        </select>

        {["max", "min", "rain"].map((metric) => (
          <motion.button
            key={metric}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => toggleMetric(metric)}
            style={{
              padding: "8px 12px",
              borderRadius: 6,
              border: `1px solid ${COLORS.border}`,
              backgroundColor: activeMetrics[metric]
                ? "#4ecdc4"
                : COLORS.cardBg,
              color: activeMetrics[metric]
                ? "#fff"
                : COLORS.text,
              cursor: "pointer",
              fontSize: 12,
              fontWeight: activeMetrics[metric] ? 600 : 400,
              transition: "all 0.2s",
            }}
          >
            {metric === "max"
              ? "Max Temp"
              : metric === "min"
                ? "Min Temp"
                : "Rain %"}
          </motion.button>
        ))}
      </motion.div>

      <motion.div variants={chartVariants}>{renderChart()}</motion.div>
    </motion.div>
  );
};

export default AdvancedForecastChart;
