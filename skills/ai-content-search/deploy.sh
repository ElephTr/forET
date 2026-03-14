#!/bin/bash
# AI 内容搜索工具部署脚本

echo "🚀 部署 AI 内容聚合搜索工具..."

# 检查 Tomcat
if [ -d "/opt/apache-tomcat-10.1.34" ]; then
    TOMCAT_WEBAPPS="/opt/apache-tomcat-10.1.34/webapps"
elif [ -d "/var/lib/tomcat9" ]; then
    TOMCAT_WEBAPPS="/var/lib/tomcat9/webapps"
elif [ -d "/usr/share/tomcat" ]; then
    TOMCAT_WEBAPPS="/usr/share/tomcat/webapps"
else
    echo "❌ 未找到 Tomcat，请先安装"
    exit 1
fi

# 创建部署目录
DEPLOY_DIR="$TOMCAT_WEBAPPS/ai-search"
mkdir -p "$DEPLOY_DIR"

# 复制文件
cp -r scripts "$DEPLOY_DIR/"
cp SKILL.md "$DEPLOY_DIR/"
cp skill.json "$DEPLOY_DIR/"

# 创建 index.html 跳转
cat > "$DEPLOY_DIR/index.html" << 'HTMLEOF'
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="0;url=scripts/web_server.py">
    <title>AI 内容搜索</title>
</head>
<body>
    <p>正在启动...</p>
    <p>如果未自动跳转，请 <a href="http://localhost:8888">点击这里</a></p>
</body>
</html>
HTMLEOF

echo "✅ 部署完成！"
echo ""
echo "启动方式:"
echo "  1. 直接运行: python3 scripts/web_server.py"
echo "  2. 访问: http://localhost:8888"
echo ""
echo "命令行使用:"
echo "  python3 scripts/search.py 'AI 工具'"
echo "  python3 scripts/search.py 'ChatGPT' --platforms reddit,zhihu"