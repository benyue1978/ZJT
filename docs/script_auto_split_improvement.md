# 剧本节点自动拆分分镜功能改进

## 更新日期
- 2026年2月3日：自动生成分镜功能
- 2026年2月4日：新增"旁白视为对话"功能

## 功能概述

优化了剧本节点的"拆分镜组"功能，使其更加智能和便捷。现在点击"拆分镜组"按钮后，系统会自动完成以下操作：

1. **检查重复拆分**：检测剧本节点下是否已有分镜组节点，避免重复拆分
2. **自动生成分镜**：为每个分镜组自动调用"生成分镜"功能，无需手动点击
3. **旁白视为对话**：支持将剧本中的旁白内容自动转换为角色"旁白"的对话

## 功能改进详情

### 1. 重复拆分检测

**改进前**：
- 用户可以多次点击"拆分镜组"按钮
- 每次点击都会创建新的分镜组节点
- 导致重复的分镜组和混乱的工作流

**改进后**：
- 点击"拆分镜组"前，系统会检查是否已存在分镜组节点
- 如果已有分镜组，显示提示："已有分镜组，请勿重复点击"
- 防止用户误操作导致的重复拆分

**实现逻辑**：
```javascript
// 检查是否已有分镜组节点
const existingShotGroups = state.connections.filter(c => c.from === id);
if(existingShotGroups.length > 0) {
  const hasShotGroupNode = existingShotGroups.some(conn => {
    const targetNode = state.nodes.find(n => n.id === conn.to);
    return targetNode && targetNode.type === 'shot_group';
  });
  
  if(hasShotGroupNode) {
    showToast('已有分镜组，请勿重复点击', 'warning');
    return;
  }
}
```

### 2. 自动生成分镜

**改进前**：
- 拆分镜组后，需要手动点击每个分镜组的"生成分镜"按钮
- 对于包含多个分镜组的剧本，操作繁琐

**改进后**：
- 拆分镜组后，自动为每个分镜组生成分镜节点
- 状态提示实时更新，显示生成进度
- 完成后显示总结信息

**实现逻辑**：
```javascript
// 创建分镜组节点数组
const createdShotGroupNodes = [];
result.data.shot_groups.forEach((shotGroup, index) => {
  const shotGroupNodeId = createShotGroupNode({...});
  if(shotGroupNodeId) {
    createdShotGroupNodes.push(shotGroupNodeId);
  }
});

// 自动为每个分镜组生成分镜
statusEl.textContent = '正在自动生成分镜...';
for(const shotGroupNodeId of createdShotGroupNodes) {
  const shotGroupNode = state.nodes.find(n => n.id === shotGroupNodeId);
  if(shotGroupNode) {
    await generateShotFramesIndependentAsync(shotGroupNodeId, shotGroupNode);
  }
}
statusEl.textContent = `已完成：${createdShotGroupNodes.length}个分镜组，所有分镜已自动生成`;
```

### 3. 新增异步生成函数

为了支持自动批量生成分镜，新增了 `generateShotFramesIndependentAsync` 函数：

**特点**：
- 异步执行，支持在循环中使用 `await`
- 与原有的 `generateShotFramesIndependent` 函数逻辑相同
- 不显示 Toast 提示，避免批量生成时的提示信息过多
- 返回创建的分镜节点数量

**函数签名**：
```javascript
async function generateShotFramesIndependentAsync(shotGroupNodeId, shotGroupNode)
```

## 用户体验改进

### 操作流程对比

**改进前**：
1. 点击"拆分镜组"
2. 等待LLM解析剧本
3. 手动点击第1个分镜组的"生成分镜"
4. 手动点击第2个分镜组的"生成分镜"
5. ...（重复N次）

**改进后**：
1. 点击"拆分镜组"
2. 等待LLM解析剧本
3. 系统自动生成所有分镜
4. 完成！

### 状态提示优化

拆分过程中的状态提示：
- "正在调用LLM解析剧本..."
- "解析成功！共N个分镜组"
- "正在自动生成分镜..."
- "已完成：N个分镜组，所有分镜已自动生成"

最终提示：
- "剧本拆分成功！所有分镜已自动生成"

## 技术实现

### 修改的文件

**`/web/js/nodes.js`**

1. **修改位置**：剧本节点的 `splitBtn` 点击事件处理函数（约3798-3931行）

2. **主要改动**：
   - 添加重复拆分检测逻辑（3806-3818行）
   - 收集创建的分镜组节点ID（3875行）
   - 自动调用生成分镜函数（3908-3917行）
   - 更新状态提示文本（3909、3916-3917、3920行）

3. **新增函数**：`generateShotFramesIndependentAsync`（约4190-4262行）
   - 异步版本的分镜生成函数
   - 用于批量自动生成分镜

### 代码结构

```
剧本节点 (Script Node)
├─ 拆分镜组按钮点击事件
│  ├─ 检查是否已有分镜组 ✨ 新增
│  ├─ 调用API解析剧本
│  ├─ 创建分镜组节点
│  ├─ 自动生成分镜 ✨ 新增
│  │  └─ generateShotFramesIndependentAsync() ✨ 新增
│  └─ 更新状态提示
```

## 注意事项

1. **检测范围**：只检测直接连接到剧本节点的分镜组，不检测间接连接
2. **异步执行**：自动生成分镜是异步执行的，按顺序依次生成每个分镜组
3. **错误处理**：如果某个分镜组生成失败，不会影响其他分镜组的生成
4. **性能考虑**：对于包含大量分镜的剧本，自动生成可能需要较长时间

## 兼容性

- 与现有的手动"生成分镜"功能完全兼容
- 不影响已有的工作流数据
- 支持工作流的保存和加载

## 旁白视为对话功能（2026年2月4日新增）

### 功能说明

在剧本节点中新增"旁白视为对话"选项，启用后系统会自动将剧本中的旁白内容转换为角色"旁白"的对话。

### 使用场景

适用于需要为旁白内容生成配音的场景，例如：
- 纪录片风格的视频
- 故事叙述类视频
- 需要画外音解说的视频

### 功能特点

1. **自动识别旁白**：
   - 识别剧本中标注为"旁白台本"、"旁白"、"narration"的内容
   - 识别"画面描述"中的叙述性文字
   - 识别非角色对话的叙述性文字

2. **自动创建旁白角色**：
   - 角色ID：`char_narrator`
   - 角色名称：旁白
   - 角色类型：旁白
   - 描述：剧本旁白角色，用于叙述画面描述和背景信息

3. **对话格式转换**：
   - 将旁白内容添加到对应镜头的dialogue数组中
   - 格式：`{"character_id": "char_narrator", "character_name": "【【旁白】】", "text": "旁白内容"}`

### 使用示例

**原剧本内容**：
```
**【画面描述】**
航拍视角。清晨的阳光洒在如森林般的摩天大楼上。镜头快速穿梭，最后停留在正走向顶级西餐厅"云端之上"的男人身上。

**【旁白台本】**
注意看，这个男人叫苏晨。
他刚刚发现，自己穿越到了一个疯掉的世界。
这里的货币价值疯涨了亿万倍，金钱的购买力产生了降维打击般的膨胀。
```

**启用"旁白视为对话"后的解析结果**：
- 在characters数组中自动添加"旁白"角色
- 在对应镜头的dialogue数组中添加旁白对话
- 旁白内容可以通过"文字转语音"节点生成配音

### 前端实现

**位置**：`/web/js/nodes.js`

1. **HTML选项**（约3887-3893行）：
```javascript
<div class="field field-collapsible">
  <label style="display: flex; align-items: center; gap: 8px; cursor: pointer; font-size: 13px;">
    <input type="checkbox" class="script-narration-as-dialogue" style="cursor: pointer;" />
    <span>旁白视为对话</span>
  </label>
  <div class="gen-meta" style="margin-top: 4px; font-size: 11px; color: #666;">将剧本中的旁白内容视为角色"旁白"的对话</div>
</div>
```

2. **数据初始化**（约3944行）：
```javascript
node.data.narrationAsDialogue = false;
```

3. **事件监听**（约4023-4026行）：
```javascript
narrationAsDialogueEl.addEventListener('change', () => {
  node.data.narrationAsDialogue = narrationAsDialogueEl.checked;
});
```

4. **API调用**（约4133、4657行）：
```javascript
narration_as_dialogue: node.data.narrationAsDialogue || false
```

### 后端实现

**位置**：`/home/appuser/comfyui_server_dev2/`

1. **API接口**（`server.py`，约4489、4540行）：
```python
narration_as_dialogue = body.get('narration_as_dialogue', False)

parsed_data = await parse_script_to_shots(
    # ...
    narration_as_dialogue=narration_as_dialogue,
    # ...
)
```

2. **剧本解析模块**（`llm/script_parser.py`）：
   - 函数签名添加`narration_as_dialogue`参数（约334行）
   - 在提示词中添加旁白处理规则（约549-598行）
   - LLM会根据提示词自动识别和转换旁白内容

### 注意事项

1. **默认关闭**：该选项默认不启用，需要用户手动勾选
2. **与其他选项兼容**：可以与"对话禁止全景"、"拆分多人对话镜头"等选项同时使用
3. **旁白角色固定**：系统会自动创建ID为`char_narrator`的旁白角色，无需手动创建
4. **配音生成**：旁白对话可以通过"文字转语音"节点生成配音，与普通角色对话一样处理

## 未来优化方向

1. **并行生成**：考虑支持并行生成多个分镜组（需评估服务器负载）
2. **进度条**：添加更详细的进度条显示
3. **取消功能**：支持取消正在进行的自动生成
4. **选择性生成**：允许用户选择要生成的分镜组
5. **旁白音色定制**：支持为旁白角色设置专门的音色和语速
