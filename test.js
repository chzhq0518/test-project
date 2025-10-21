/**
 * GitHub MCP Server 测试项目
 * JavaScript 测试文件
 */

class TestProject {
    constructor() {
        this.name = "test-project";
        this.version = "1.0.0";
        this.description = "用于测试GitHub MCP Server功能";
    }

    /**
     * 测试方法
     * @returns {string} 测试结果
     */
    test() {
        console.log("Hello from test-project!");
        console.log(`项目名称: ${this.name}`);
        console.log(`版本: ${this.version}`);
        console.log(`描述: ${this.description}`);
        console.log(`当前时间: ${new Date().toLocaleString()}`);
        return "JavaScript测试成功";
    }

    /**
     * 获取项目信息
     * @returns {Object} 项目信息对象
     */
    getInfo() {
        return {
            name: this.name,
            version: this.version,
            description: this.description,
            timestamp: new Date().toISOString()
        };
    }
}

// 创建测试实例
const testProject = new TestProject();

// 运行测试
console.log("=== GitHub MCP Server 测试项目 ===");
const result = testProject.test();
console.log(`测试结果: ${result}`);

// 导出模块（如果使用Node.js）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TestProject;
}