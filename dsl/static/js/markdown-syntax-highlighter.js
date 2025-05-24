/**
 * Markdown Syntax Highlighter
 * 
 * This script automatically applies syntax highlighting to code blocks in Markdown files.
 * It uses Prism.js for syntax highlighting and automatically detects the language from
 * the code block's class.
 * 
 * Usage:
 * 1. Include this script in your HTML after including Prism.js
 * 2. It will automatically highlight all code blocks in markdown content
 * 3. For best results, include the appropriate Prism.js language components
 */

class MarkdownSyntaxHighlighter {
    constructor(options = {}) {
        this.options = Object.assign({
            codeBlockSelector: 'pre code',
            supportedLanguages: [
                'python', 'javascript', 'typescript', 'bash', 'shell', 'cmd', 'powershell',
                'json', 'yaml', 'html', 'css', 'sql', 'csharp', 'java', 'php', 'ruby',
                'go', 'rust', 'swift', 'kotlin', 'scala', 'perl', 'r', 'matlab',
                'dsl', 'flow', 'makefile', 'dockerfile', 'xml', 'markdown', 'plaintext'
            ],
            defaultLanguage: 'plaintext',
            theme: 'default', // 'default', 'dark', 'okaidia', etc.
            lineNumbers: true,
            copyButton: true
        }, options);

        // Map of language aliases
        this.languageAliases = {
            'py': 'python',
            'js': 'javascript',
            'ts': 'typescript',
            'sh': 'bash',
            'yml': 'yaml',
            'cs': 'csharp',
            'md': 'markdown',
            'rb': 'ruby',
            'pl': 'perl',
            'ps': 'powershell',
            'ps1': 'powershell',
            'bat': 'cmd',
            'cmd': 'cmd',
            'c#': 'csharp',
            'shell': 'bash',
            'text': 'plaintext',
            'txt': 'plaintext'
        };

        this.init();
    }

    init() {
        // Check if Prism is loaded
        if (typeof Prism === 'undefined') {
            this.loadPrism();
        } else {
            this.highlightCodeBlocks();
        }

        // Add CSS for copy button if enabled
        if (this.options.copyButton) {
            this.addCopyButtonStyles();
        }
    }

    loadPrism() {
        // Create script element for Prism.js
        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js';
        script.onload = () => {
            // Load theme
            this.loadPrismTheme();
            
            // Load line numbers plugin if enabled
            if (this.options.lineNumbers) {
                this.loadPrismPlugin('line-numbers');
            }
            
            // Load language components for supported languages
            this.loadLanguageComponents();
            
            // Highlight code blocks once everything is loaded
            this.highlightCodeBlocks();
        };
        document.head.appendChild(script);
    }

    loadPrismTheme() {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = `https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism${this.options.theme !== 'default' ? `-${this.options.theme}` : ''}.min.css`;
        document.head.appendChild(link);
    }

    loadPrismPlugin(plugin) {
        // Load plugin CSS
        const cssLink = document.createElement('link');
        cssLink.rel = 'stylesheet';
        cssLink.href = `https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/${plugin}/prism-${plugin}.min.css`;
        document.head.appendChild(cssLink);
        
        // Load plugin JS
        const script = document.createElement('script');
        script.src = `https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/${plugin}/prism-${plugin}.min.js`;
        document.head.appendChild(script);
    }

    loadLanguageComponents() {
        // Load language components for all supported languages
        this.options.supportedLanguages.forEach(lang => {
            if (lang !== 'plaintext' && lang !== this.options.defaultLanguage) {
                const script = document.createElement('script');
                script.src = `https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-${lang}.min.js`;
                document.head.appendChild(script);
            }
        });
    }

    highlightCodeBlocks() {
        // Find all code blocks
        const codeBlocks = document.querySelectorAll(this.options.codeBlockSelector);
        
        codeBlocks.forEach(codeBlock => {
            // Skip if already highlighted
            if (codeBlock.classList.contains('prism-highlighted')) return;
            
            // Determine language from class
            let language = this.detectLanguage(codeBlock);
            
            // Add appropriate class for Prism
            if (language && !codeBlock.classList.contains(`language-${language}`)) {
                codeBlock.classList.add(`language-${language}`);
            }
            
            // Add line numbers if enabled
            if (this.options.lineNumbers) {
                const preElement = codeBlock.parentElement;
                if (preElement && preElement.tagName === 'PRE') {
                    preElement.classList.add('line-numbers');
                }
            }
            
            // Add copy button if enabled
            if (this.options.copyButton) {
                this.addCopyButton(codeBlock);
            }
            
            // Mark as highlighted to avoid processing again
            codeBlock.classList.add('prism-highlighted');
        });
        
        // Trigger Prism to highlight all code blocks
        if (typeof Prism !== 'undefined') {
            Prism.highlightAll();
        }
    }

    detectLanguage(codeBlock) {
        // Check for language class (language-*)
        for (const className of codeBlock.classList) {
            if (className.startsWith('language-')) {
                const lang = className.replace('language-', '');
                // Return the language or its alias if it exists
                return this.languageAliases[lang] || lang;
            }
        }
        
        // Try to detect language from content
        const content = codeBlock.textContent.trim();
        
        // Check for common patterns
        if (content.startsWith('import ') || content.startsWith('from ') || content.includes('def ') || content.includes('class ')) {
            return 'python';
        } else if (content.startsWith('function ') || content.includes('const ') || content.includes('let ') || content.includes('var ')) {
            return 'javascript';
        } else if (content.startsWith('<!DOCTYPE html>') || content.startsWith('<html>')) {
            return 'html';
        } else if (content.startsWith('<?php')) {
            return 'php';
        } else if (content.startsWith('package ') || content.includes('public class ')) {
            return 'java';
        } else if (content.startsWith('using ') && content.includes(';')) {
            return 'csharp';
        } else if (content.startsWith('SELECT ') || content.startsWith('INSERT ') || content.startsWith('UPDATE ')) {
            return 'sql';
        } else if (content.startsWith('#!/bin/bash') || content.startsWith('#!/bin/sh')) {
            return 'bash';
        } else if (content.startsWith('flow ')) {
            return 'dsl';
        }
        
        // Default to plaintext if no language detected
        return this.options.defaultLanguage;
    }

    addCopyButton(codeBlock) {
        const preElement = codeBlock.parentElement;
        if (!preElement || preElement.tagName !== 'PRE') return;
        
        // Create copy button
        const copyButton = document.createElement('button');
        copyButton.className = 'copy-code-button';
        copyButton.textContent = 'Copy';
        
        // Add click event
        copyButton.addEventListener('click', () => {
            // Copy code to clipboard
            const code = codeBlock.textContent;
            navigator.clipboard.writeText(code).then(() => {
                // Change button text temporarily
                copyButton.textContent = 'Copied!';
                setTimeout(() => {
                    copyButton.textContent = 'Copy';
                }, 2000);
            }).catch(err => {
                console.error('Failed to copy code: ', err);
                copyButton.textContent = 'Error';
                setTimeout(() => {
                    copyButton.textContent = 'Copy';
                }, 2000);
            });
        });
        
        // Add button to pre element
        preElement.style.position = 'relative';
        preElement.appendChild(copyButton);
    }

    addCopyButtonStyles() {
        // Add CSS for copy button
        const style = document.createElement('style');
        style.textContent = `
            pre {
                position: relative;
            }
            
            .copy-code-button {
                position: absolute;
                top: 5px;
                right: 5px;
                background-color: #f5f5f5;
                border: 1px solid #ccc;
                border-radius: 3px;
                color: #333;
                font-size: 0.8em;
                padding: 3px 8px;
                cursor: pointer;
                opacity: 0;
                transition: opacity 0.3s;
            }
            
            pre:hover .copy-code-button {
                opacity: 1;
            }
            
            .copy-code-button:hover {
                background-color: #e0e0e0;
            }
            
            .copy-code-button:active {
                background-color: #d0d0d0;
            }
        `;
        document.head.appendChild(style);
    }
}

// Initialize the highlighter when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new MarkdownSyntaxHighlighter();
});

// Add a global function to manually initialize the highlighter
window.initMarkdownSyntaxHighlighter = function(options) {
    return new MarkdownSyntaxHighlighter(options);
};
