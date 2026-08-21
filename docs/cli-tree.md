# CLI 树

`ChatHFD` 当前是 root-only CLI。这个页面必须从真实 `chathfd --tree` 输出同步，不能手写未来命令。ChatStyle 共享 Click tree runtime 将公开根名固定为 `chathfd`。

```text
chathfd
├── --help  # Show this message and exit.
├── --version  # Show the version and exit.
├── --tree  # Print the registered CLI tree and exit.
└── --tree-brief  # Print the registered CLI tree without parameter signatures and exit.
```

`--tree` 默认保留命令参数签名；`--tree-brief` 省略参数签名，同时保留命令节点和描述。当前没有参数化子命令，因此两种模式显示同一组 root-only 节点。

## 当前状态

| 入口 | 状态 | 说明 |
| --- | --- | --- |
| `chathfd --help` | 已实现 | 显示根命令帮助。 |
| `chathfd --version` | 已实现 | 显示已安装包版本。 |
| `chathfd --tree` | 已实现 | 显示带命令参数签名的当前真实 CLI 树。 |
| `chathfd --tree-brief` | 已实现 | 显示省略命令参数签名的当前真实 CLI 树。 |
| HFD 下载子命令 | 尚未实现 | 未来有实际下载编排能力后再加入 CLI。 |

## 更新规则

新增真实命令时，先更新 Click 注册面和测试，再运行 `chathfd --tree` 和 `chathfd --tree-brief` 回填 README 与本页。
