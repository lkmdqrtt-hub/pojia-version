# 网络小白一键破甲 · 版本清单仓库

这个仓库只放一个东西：`version.json`。

客户端启动时拉它，用来做四件事：

1. 比对人格指纹，决定要不要重新下载人格
2. 显示公告
3. 检查版本是否过旧
4. 拉赞赏码

**人格正文不在这里。** 人格放在 Cloudflare Workers（`persona.gzdqrtt.online`），
仓库里只有它的 sha256 指纹。

## 为什么只有公开信息

这个仓库是公开的，任何人能看到全部内容。所以这里只能放：

- 版本号
- 公告文字
- 赞赏码图片
- 官方链接

不能放：人格正文、密钥、令牌、后台密码。

## 文件结构

```
pojia-version/
├── version.json        客户端唯一读取的文件
├── donate.png          赞赏码（可选，version.json 里登记 sha256）
├── README.md           本文件
└── LICENSE             MIT
```

## 谁在写这个文件

**不要手改 `version.json`。** 它有 Ed25519 签名，手改之后客户端验签失败，
会静默回落到内置副本——不报错，但更新和公告全部不生效，很难查。

正确流程是在自己机器上跑 `repo-tools/build_version.py`，见
`网络小白一键破甲-网络版-v1.0.0\维护手册.md`。

## 客户端读取地址（按顺序回退）

```
https://cdn.jsdelivr.net/gh/<user>/pojia-version@main/version.json
https://ghproxy.net/https://raw.githubusercontent.com/<user>/pojia-version/main/version.json
https://raw.githubusercontent.com/<user>/pojia-version/main/version.json
```

jsDelivr 国内最快，但缓存约 12 小时；raw 约 5 分钟生效。三个都失败就用本地缓存。

## 免费声明

本软件永久免费，不通过任何渠道销售。
任何向你收费出售本软件的行为均为诈骗。

官方地址：https://github.com/lkmdqrtt-hub/pojia-version

## 许可

MIT。基于 [pojia-next](https://github.com/z91772524-ai/pojia-next)
（作者 z91772524-ai）二次修改。
