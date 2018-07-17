# 分支意义

```

master

    意义：生产环境分支

    时效性：永久

    更新策略：不可直接提交源代码，只可以通过合并可靠的 issue 分支来更新自身

    可靠性：可靠分支

staging

    意义：统一测试环境分支

    时效性：永久

    更新策略：原则上不可直接提交源代码，自动合并任意一次提交的任意 issue 分支，确保为统一测试环境提供一份兼容所有开发者的最新代码

    可靠性：不可靠/可靠分支

issue 分支

    意义：开发者分支

    时效性：临时

    更新策略：直接 commit 源代码，不可合并其他分支

    可靠性：不可靠/可靠分支

```

---

# 一个发布周期涉及的分支操作

```

* Admin 新建 issue

* Developer 更新本地 master 分支

* Developer 在 master 分支基础上新建 issue 分支

* Developer 推送 issue 分支到远端

* Developer 进行开发

* Developer 完成开发， issue 留言，新建 mr（mr 命名统一 # 号加上 issue 号），请求 master 分支合并 issue 分支，并指派 Reviewer

* Reviewer 进行 review

* Reviewer 完成 review，通知 Admin

* Admin 结束 MR，master 分支合并 issue 分支，删除 issue 分支

* Admin 给 master 分支打标签 

```
