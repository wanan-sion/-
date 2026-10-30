# 架构设计说明

## 设计目标

面向边缘 / 低资源场景，构建一个"感知 → 理解 → 交互"的多模态轻量闭环。核心约束：

1. **轻量**：核心功能零第三方硬依赖，纯标准库可运行；
2. **可扩展**：感知器、识别器、推理器均为插件式接口，可无痛替换为轻量模型实现；
3. **统一**：多模态输入统一收敛为结构化 `PerceptionEvent`，引擎不感知模态差异。

## 三层架构

```
┌──────────────────────────────────────────────────────────┐
│ 交互层 Interaction   DialogueManager / OutputFormatter   │
│   多轮编排 · 会话历史 · CLI / REST API 输出             │
├──────────────────────────────────────────────────────────┤
│ 理解层 Engine        IntentRecognizer / RuleReasoner    │
│   多模态融合 · 意图识别 · 轻量推理 / 回复               │
├──────────────────────────────────────────────────────────┤
│ 感知层 Perception    Vision / Audio / Text Perceiver    │
│   信号 → PerceptionEvent · 可注入轻量模型               │
├──────────────────────────────────────────────────────────┤
│ 适配层 Adapters      ONNX / TFLite / ASR / LLM 回调     │
└──────────────────────────────────────────────────────────┘
```

## 数据流

一次交互的数据流：

```text
用户输入
   │  DialogueManager.turn()
   ├── TextPerceiver.analyze()      → text 事件
   ├── (可选) VisionPerceiver       → vision 事件
   ├── (可选) AudioPerceiver        → audio 事件
   ▼
IntentRecognizer.recognize(events)  → Intent（含置信度、命中的信号词、各模态详情）
   ▼
RuleReasoner.reply(intent)          → 自然语言回复
   ▼
OutputFormatter.format(...)         → 结构化结果 / 控制台文本
```

## 关键设计决策

| 决策 | 理由 |
|------|------|
| 统一 `PerceptionEvent` 事件结构 | 让引擎对模态无关，新增模态只加感知器 |
| 感知器支持注入模型回调 | 规则实现可平滑升级为轻量模型，接口稳定 |
| 可选依赖 + 自动回退 | 保证任何环境都能启动，增强能力按需开启 |
| 内置标准库测试 | 无需额外测试框架即可验证核心闭环 |
