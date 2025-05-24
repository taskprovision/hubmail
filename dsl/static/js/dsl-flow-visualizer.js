/**
 * DSL Flow Visualizer
 * 
 * This script renders Taskinity DSL flow definitions as SVG diagrams.
 * It automatically finds DSL code blocks in Markdown and renders them as visual workflows.
 * 
 * Usage:
 * 1. Include this script in your HTML
 * 2. Add class "dsl-flow" to any code block containing DSL
 * 3. The script will automatically render SVG diagrams below the code blocks
 */

class DSLFlowVisualizer {
    constructor(options = {}) {
        this.options = Object.assign({
            codeBlockSelector: 'pre code.language-dsl, pre code.language-flow',
            containerClass: 'dsl-flow-diagram',
            nodeWidth: 180,
            nodeHeight: 60,
            nodePadding: 15,
            horizontalSpacing: 100,
            verticalSpacing: 80,
            arrowSize: 10,
            colors: {
                node: {
                    fill: '#f0f8ff',
                    stroke: '#4682b4',
                    text: '#333333',
                    highlight: '#6ca0dc'
                },
                arrow: {
                    stroke: '#4682b4',
                    fill: '#4682b4'
                },
                description: {
                    text: '#666666'
                }
            },
            fonts: {
                node: '14px Arial, sans-serif',
                description: '12px Arial, sans-serif'
            }
        }, options);

        this.init();
    }

    init() {
        // Find all DSL code blocks
        const codeBlocks = document.querySelectorAll(this.options.codeBlockSelector);
        
        // Process each code block
        codeBlocks.forEach(codeBlock => {
            const dslCode = codeBlock.textContent.trim();
            const flowData = this.parseDSL(dslCode);
            
            if (flowData) {
                // Create container for the diagram
                const container = document.createElement('div');
                container.className = this.options.containerClass;
                
                // Insert container after the code block
                const preElement = codeBlock.closest('pre');
                preElement.parentNode.insertBefore(container, preElement.nextSibling);
                
                // Render the diagram
                this.renderDiagram(container, flowData);
            }
        });
    }

    parseDSL(dslCode) {
        // Basic DSL parser
        const flowMatch = dslCode.match(/flow\s+([A-Za-z0-9_]+):/);
        if (!flowMatch) return null;
        
        const flowName = flowMatch[1];
        const lines = dslCode.split('\n');
        
        let description = '';
        const descriptionMatch = dslCode.match(/description:\s*"([^"]+)"/);
        if (descriptionMatch) {
            description = descriptionMatch[1];
        }
        
        // Extract tasks and connections
        const tasks = new Set();
        const connections = [];
        
        lines.forEach(line => {
            // Match connections (task1 -> task2)
            const connectionMatch = line.match(/\s*([A-Za-z0-9_]+)\s*->\s*([A-Za-z0-9_]+)/);
            if (connectionMatch) {
                const source = connectionMatch[1];
                const target = connectionMatch[2];
                
                tasks.add(source);
                tasks.add(target);
                connections.push({ source, target });
            }
            
            // Match task definitions (task TaskName:)
            const taskMatch = line.match(/\s*task\s+([A-Za-z0-9_]+):/);
            if (taskMatch) {
                tasks.add(taskMatch[1]);
            }
        });
        
        return {
            name: flowName,
            description: description,
            tasks: Array.from(tasks),
            connections: connections
        };
    }

    renderDiagram(container, flowData) {
        // Calculate layout
        const layout = this.calculateLayout(flowData);
        
        // Create SVG
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('width', layout.width);
        svg.setAttribute('height', layout.height);
        svg.setAttribute('class', 'dsl-flow-svg');
        
        // Add title
        const title = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        title.setAttribute('x', layout.width / 2);
        title.setAttribute('y', 30);
        title.setAttribute('text-anchor', 'middle');
        title.setAttribute('font-weight', 'bold');
        title.setAttribute('font-size', '16px');
        title.textContent = `Flow: ${flowData.name}`;
        svg.appendChild(title);
        
        // Add description if available
        if (flowData.description) {
            const description = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            description.setAttribute('x', layout.width / 2);
            description.setAttribute('y', 50);
            description.setAttribute('text-anchor', 'middle');
            description.setAttribute('fill', this.options.colors.description.text);
            description.setAttribute('font', this.options.fonts.description);
            description.textContent = flowData.description;
            svg.appendChild(description);
        }
        
        // Create connections (arrows)
        const arrowsGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        arrowsGroup.setAttribute('class', 'connections');
        
        flowData.connections.forEach(connection => {
            const sourceNode = layout.nodes[connection.source];
            const targetNode = layout.nodes[connection.target];
            
            if (sourceNode && targetNode) {
                const arrow = this.createArrow(sourceNode, targetNode);
                arrowsGroup.appendChild(arrow);
            }
        });
        
        svg.appendChild(arrowsGroup);
        
        // Create nodes
        const nodesGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        nodesGroup.setAttribute('class', 'nodes');
        
        Object.entries(layout.nodes).forEach(([taskName, nodePos]) => {
            const node = this.createNode(taskName, nodePos);
            nodesGroup.appendChild(node);
        });
        
        svg.appendChild(nodesGroup);
        
        // Add to container
        container.appendChild(svg);
        
        // Add download button
        const downloadBtn = document.createElement('button');
        downloadBtn.textContent = 'Download SVG';
        downloadBtn.className = 'dsl-download-btn';
        downloadBtn.style.marginTop = '10px';
        downloadBtn.style.padding = '5px 10px';
        downloadBtn.style.cursor = 'pointer';
        
        downloadBtn.addEventListener('click', () => {
            this.downloadSVG(svg, flowData.name);
        });
        
        container.appendChild(downloadBtn);
    }

    calculateLayout(flowData) {
        // Analyze the graph structure to determine levels
        const levels = this.analyzeLevels(flowData);
        
        // Calculate node positions based on levels
        const nodes = {};
        let maxNodesInLevel = 0;
        
        Object.entries(levels).forEach(([level, taskNames]) => {
            maxNodesInLevel = Math.max(maxNodesInLevel, taskNames.length);
            
            taskNames.forEach((taskName, index) => {
                const levelNum = parseInt(level);
                const x = this.options.horizontalSpacing + levelNum * (this.options.nodeWidth + this.options.horizontalSpacing);
                
                // Center nodes vertically within their level
                const levelHeight = taskNames.length * (this.options.nodeHeight + this.options.verticalSpacing) - this.options.verticalSpacing;
                const startY = (levelNum === 0 ? 80 : 60) + (maxNodesInLevel * (this.options.nodeHeight + this.options.verticalSpacing) - levelHeight) / 2;
                const y = startY + index * (this.options.nodeHeight + this.options.verticalSpacing);
                
                nodes[taskName] = {
                    x: x,
                    y: y,
                    width: this.options.nodeWidth,
                    height: this.options.nodeHeight
                };
            });
        });
        
        // Calculate SVG dimensions
        const maxLevel = Math.max(...Object.keys(levels).map(l => parseInt(l)));
        const width = this.options.horizontalSpacing * 2 + (maxLevel + 1) * (this.options.nodeWidth + this.options.horizontalSpacing);
        const height = (maxNodesInLevel + 1) * (this.options.nodeHeight + this.options.verticalSpacing) + 60;
        
        return {
            nodes: nodes,
            width: width,
            height: height
        };
    }

    analyzeLevels(flowData) {
        // Find root nodes (nodes with no incoming connections)
        const hasIncoming = new Set();
        flowData.connections.forEach(conn => {
            hasIncoming.add(conn.target);
        });
        
        const roots = flowData.tasks.filter(task => !hasIncoming.has(task));
        
        // Initialize levels
        const levels = { 0: roots };
        const assigned = new Set(roots);
        
        // Assign levels to the rest of the nodes
        let currentLevel = 0;
        while (assigned.size < flowData.tasks.length) {
            const nextLevel = [];
            
            levels[currentLevel].forEach(source => {
                // Find all targets of this source
                flowData.connections
                    .filter(conn => conn.source === source)
                    .forEach(conn => {
                        if (!assigned.has(conn.target)) {
                            nextLevel.push(conn.target);
                            assigned.add(conn.target);
                        }
                    });
            });
            
            if (nextLevel.length === 0) {
                // Handle disconnected nodes or cycles
                const unassigned = flowData.tasks.filter(task => !assigned.has(task));
                if (unassigned.length > 0) {
                    nextLevel.push(...unassigned);
                    unassigned.forEach(task => assigned.add(task));
                }
            }
            
            if (nextLevel.length > 0) {
                currentLevel++;
                levels[currentLevel] = nextLevel;
            } else {
                break;
            }
        }
        
        return levels;
    }

    createNode(taskName, nodePos) {
        const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        group.setAttribute('class', 'node');
        group.setAttribute('data-task', taskName);
        
        // Create node rectangle
        const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        rect.setAttribute('x', nodePos.x);
        rect.setAttribute('y', nodePos.y);
        rect.setAttribute('width', nodePos.width);
        rect.setAttribute('height', nodePos.height);
        rect.setAttribute('rx', '5');
        rect.setAttribute('ry', '5');
        rect.setAttribute('fill', this.options.colors.node.fill);
        rect.setAttribute('stroke', this.options.colors.node.stroke);
        rect.setAttribute('stroke-width', '2');
        
        // Create node text
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', nodePos.x + nodePos.width / 2);
        text.setAttribute('y', nodePos.y + nodePos.height / 2);
        text.setAttribute('text-anchor', 'middle');
        text.setAttribute('dominant-baseline', 'middle');
        text.setAttribute('fill', this.options.colors.node.text);
        text.setAttribute('font', this.options.fonts.node);
        text.textContent = taskName;
        
        // Add hover effects
        group.addEventListener('mouseover', () => {
            rect.setAttribute('fill', this.options.colors.node.highlight);
        });
        
        group.addEventListener('mouseout', () => {
            rect.setAttribute('fill', this.options.colors.node.fill);
        });
        
        group.appendChild(rect);
        group.appendChild(text);
        
        return group;
    }

    createArrow(sourceNode, targetNode) {
        const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        group.setAttribute('class', 'arrow');
        
        // Calculate connection points
        const start = {
            x: sourceNode.x + sourceNode.width,
            y: sourceNode.y + sourceNode.height / 2
        };
        
        const end = {
            x: targetNode.x,
            y: targetNode.y + targetNode.height / 2
        };
        
        // Draw line
        const line = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        
        // Create a curved path if nodes are not on the same level
        let path;
        if (Math.abs(start.y - end.y) < 1) {
            // Straight line for nodes on the same level
            path = `M ${start.x} ${start.y} L ${end.x - this.options.arrowSize} ${end.y}`;
        } else {
            // Curved line for nodes on different levels
            const controlX = (start.x + end.x) / 2;
            path = `M ${start.x} ${start.y} 
                    C ${controlX} ${start.y}, ${controlX} ${end.y}, ${end.x - this.options.arrowSize} ${end.y}`;
        }
        
        line.setAttribute('d', path);
        line.setAttribute('fill', 'none');
        line.setAttribute('stroke', this.options.colors.arrow.stroke);
        line.setAttribute('stroke-width', '2');
        
        // Draw arrowhead
        const arrowHead = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
        const arrowSize = this.options.arrowSize;
        const points = [
            `${end.x},${end.y}`,
            `${end.x - arrowSize},${end.y - arrowSize / 2}`,
            `${end.x - arrowSize},${end.y + arrowSize / 2}`
        ].join(' ');
        
        arrowHead.setAttribute('points', points);
        arrowHead.setAttribute('fill', this.options.colors.arrow.fill);
        
        group.appendChild(line);
        group.appendChild(arrowHead);
        
        return group;
    }

    downloadSVG(svgElement, flowName) {
        // Create a copy of the SVG
        const svgCopy = svgElement.cloneNode(true);
        
        // Add XML declaration and namespace
        const svgData = new XMLSerializer().serializeToString(svgCopy);
        const svgBlob = new Blob([
            '<?xml version="1.0" standalone="no"?>\r\n',
            '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\r\n',
            svgData
        ], { type: 'image/svg+xml' });
        
        const svgUrl = URL.createObjectURL(svgBlob);
        
        // Create download link
        const downloadLink = document.createElement('a');
        downloadLink.href = svgUrl;
        downloadLink.download = `${flowName.replace(/\s+/g, '_')}_flow.svg`;
        document.body.appendChild(downloadLink);
        downloadLink.click();
        document.body.removeChild(downloadLink);
        
        // Clean up
        setTimeout(() => {
            URL.revokeObjectURL(svgUrl);
        }, 100);
    }
}

// Initialize the visualizer when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Add CSS styles
    const style = document.createElement('style');
    style.textContent = `
        .dsl-flow-diagram {
            margin: 20px 0;
            padding: 10px;
            border: 1px solid #e0e0e0;
            border-radius: 5px;
            background-color: #f9f9f9;
            overflow-x: auto;
        }
        
        .dsl-download-btn {
            background-color: #4682b4;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 5px 10px;
            font-size: 14px;
            cursor: pointer;
        }
        
        .dsl-download-btn:hover {
            background-color: #36648b;
        }
    `;
    document.head.appendChild(style);
    
    // Initialize the visualizer
    new DSLFlowVisualizer();
    
    // Add language class to DSL code blocks if not already present
    document.querySelectorAll('pre code').forEach(codeBlock => {
        const content = codeBlock.textContent.trim();
        if (content.startsWith('flow ') && !codeBlock.classList.contains('language-dsl')) {
            codeBlock.classList.add('language-dsl');
            // Re-initialize the visualizer to catch newly marked blocks
            new DSLFlowVisualizer();
        }
    });
});

// Add a global function to manually initialize the visualizer
window.initDSLFlowVisualizer = function(options) {
    return new DSLFlowVisualizer(options);
};
