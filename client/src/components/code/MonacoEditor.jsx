// src/components/code/MonacoEditor.jsx
import React, { useEffect, useRef } from "react";
import Editor from "@monaco-editor/react";

const MonacoEditor = ({
  value,
  onChange,
  language = "javascript",
  theme = "vs-dark",
  onMount,
  errors = [],
  options = {},
  ...props
}) => {
  const editorRef = useRef(null);
  const monacoRef = useRef(null);

  const handleEditorDidMount = (editor, monaco) => {
    editorRef.current = editor;
    monacoRef.current = monaco;

    // Configure language
    if (language === "python") {
      monaco.languages.register({ id: "python" });
    }

    // Add error markers
    if (errors.length > 0) {
      const model = editor.getModel();
      if (model) {
        const errorMarkers = errors.map((err) => ({
          startLineNumber: err.line || 1,
          startColumn: err.column || 1,
          endLineNumber: err.line || 1,
          endColumn: err.column || 100,
          message: err.message || "Error",
          severity: err.severity || monaco.MarkerSeverity.Error,
        }));

        monaco.editor.setModelMarkers(model, "validation", errorMarkers);
      }
    }

    // Call parent onMount if provided
    if (onMount) {
      onMount(editor, monaco);
    }
  };

  // Update error markers when errors change
  useEffect(() => {
    if (editorRef.current && monacoRef.current && errors.length > 0) {
      const model = editorRef.current.getModel();
      if (model) {
        const errorMarkers = errors.map((err) => ({
          startLineNumber: err.line || 1,
          startColumn: err.column || 1,
          endLineNumber: err.line || 1,
          endColumn: err.column || 100,
          message: err.message || "Error",
          severity: err.severity || monacoRef.current.MarkerSeverity.Error,
        }));

        monacoRef.current.editor.setModelMarkers(
          model,
          "validation",
          errorMarkers
        );
      }
    }
  }, [errors]);

  const defaultOptions = {
    fontSize: 14,
    minimap: { enabled: false },
    scrollBeyondLastLine: false,
    wordWrap: "on",
    automaticLayout: true,
    formatOnPaste: true,
    formatOnType: true,
    suggestOnTriggerCharacters: true,
    acceptSuggestionOnEnter: "on",
    tabSize: 2,
    insertSpaces: true,
    autoIndent: "full",
    matchBrackets: "always",
    lineNumbers: "on",
    glyphMargin: true,
    folding: true,
    lineDecorationsWidth: 10,
    renderLineHighlight: "all",
    cursorBlinking: "blink",
    cursorStyle: "line",
    cursorWidth: 2,
    ...options,
  };

  return (
    <Editor
      height="100%"
      language={language}
      value={value}
      onChange={onChange}
      onMount={handleEditorDidMount}
      theme={theme}
      options={defaultOptions}
      {...props}
    />
  );
};

export default MonacoEditor;
