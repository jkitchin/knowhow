# Emacs Lisp Style Guide Skill

A comprehensive Claude Code skill for writing professional Emacs Lisp code following the community-driven style guide by Bozhidar Batsov.

## Overview

This skill provides expert guidance on:

- **Layout and Formatting**: Proper indentation, spacing, and code organization
- **Naming Conventions**: Package prefixes, predicates, private functions
- **Syntax and Idioms**: Preferred constructs and patterns
- **Functions and Macros**: Best practices for definition and usage
- **Documentation**: Docstrings, comments, and annotations
- **Loading and Autoloading**: Module structure and dependencies
- **Interactive Commands**: Proper interactive specifications
- **Error Handling**: Signaling and catching errors appropriately

## When to Use This Skill

The skill is automatically invoked when you:

- Write or edit Emacs Lisp files (`.el`)
- Create Emacs packages or libraries
- Develop major or minor modes
- Write interactive commands
- Set up Emacs configuration
- Refactor existing Emacs Lisp code

## Features

### 1. Source Code Layout

**Proper Indentation:**
- Spaces only, never tabs
- 2-space indent for body forms
- 4-space indent for special arguments in special forms
- Vertical alignment of function arguments

**Code Organization:**
- Maximum 80 character line length
- Empty lines between top-level forms
- All closing parentheses on the same line

### 2. Naming Conventions

**Package Prefixes:**
```elisp
;; For package 'my-package':
(defun my-package-do-something ()  ; Public
  (my-package--helper))            ; Private (double-hyphen)
```

**Predicates:**
```elisp
(defun evenp (n) ...)              ; Single word: ends with 'p'
(defun buffer-live-p (buffer) ...) ; Multiple words: ends with '-p'
```

**Unused Variables:**
```elisp
(lambda (x _y) x)                  ; Prefix with underscore
```

### 3. Preferred Syntax

**High-Level Constructs:**
```elisp
;; Use when instead of (if ... (progn ...))
(when condition
  (do-something)
  (do-more))

;; Use unless for negated conditions
(unless condition
  (do-something))

;; Use increment/decrement shortcuts
(1+ x)  ; instead of (+ x 1)
(1- x)  ; instead of (- x 1)
```

### 4. Lexical Binding

**Always Enable:**
```elisp
;;; my-package.el --- Description  -*- lexical-binding: t; -*-
```

Benefits:
- Better performance
- Proper closures
- More predictable scoping
- Better optimization by byte-compiler

### 5. Documentation

**Comprehensive Docstrings:**
```elisp
(defun my-package-process (input)
  "Process INPUT and return result.

INPUT should be a string or number.
Returns the processed value as a string.

Signals an error if INPUT is invalid."
  ...)
```

**Comment Levels:**
```elisp
;;; Section Heading

;; Top-level comment explaining the following code

(defun my-function ()
  ;; Comment within function
  (let ((x 10))  ; Inline margin comment
    x))
```

### 6. Interactive Commands

**Proper Interactive Specifications:**
```elisp
(defun my-command (arg)
  "Do something with ARG."
  (interactive "sPrompt: ")
  (message "Got: %s" arg))
```

### 7. Autoloading

**Use Autoload Cookies:**
```elisp
;;;###autoload
(defun my-package-start ()
  "Start my-package."
  (interactive)
  (my-package-mode 1))
```

## File Structure

```
emacs-lisp/
├── SKILL.md              # Main skill instructions
├── QUICK_REFERENCE.md    # Quick lookup guide
├── README.md            # This file
└── examples/
    ├── package-template.el      # Complete package example
    ├── major-mode.el           # Major mode template
    ├── minor-mode.el           # Minor mode template
    └── library-functions.el    # Function examples
```

## Installation

### For Personal Use

```bash
# Using knowhow CLI
knowhow install emacs-lisp

# Or manually
mkdir -p ~/.claude/skills/emacs-lisp
cp -r . ~/.claude/skills/emacs-lisp/
```

### For Project Use

```bash
# Using knowhow CLI
knowhow install emacs-lisp --target project

# Or manually
mkdir -p .claude/skills/emacs-lisp
cp -r . .claude/skills/emacs-lisp/
```

## Quick Start

### Creating a New Package

1. **Create file with proper header:**
```elisp
;;; my-package.el --- Brief description  -*- lexical-binding: t; -*-

;; Copyright (C) 2025 Your Name

;; Author: Your Name <your.email@example.com>
;; Version: 1.0.0
;; Package-Requires: ((emacs "27.1"))
;; Keywords: convenience, tools
;; URL: https://github.com/user/my-package

;;; Commentary:

;; Longer description and usage examples.

;;; Code:
```

2. **Define customization group:**
```elisp
(defgroup my-package nil
  "My package customization."
  :group 'convenience
  :prefix "my-package-")
```

3. **Add customizable variables:**
```elisp
(defcustom my-package-option t
  "Enable some option."
  :type 'boolean
  :group 'my-package)
```

4. **Write functions with docstrings:**
```elisp
(defun my-package-helper (arg)
  "Process ARG and return result."
  (upcase arg))
```

5. **Add interactive commands with autoload:**
```elisp
;;;###autoload
(defun my-package-command ()
  "Main user-facing command."
  (interactive)
  (message "Hello from my-package!"))
```

6. **End with provide and footer:**
```elisp
(provide 'my-package)
;;; my-package.el ends here
```

## Common Patterns

### Defining a Minor Mode

```elisp
;;;###autoload
(define-minor-mode my-mode
  "Toggle my-mode."
  :lighter " My"
  :keymap (let ((map (make-sparse-keymap)))
            (define-key map (kbd "C-c m") #'my-command)
            map)
  (if my-mode
      (my-mode--enable)
    (my-mode--disable)))

(defun my-mode--enable ()
  "Enable my-mode."
  (add-hook 'post-command-hook #'my-post-command nil t))

(defun my-mode--disable ()
  "Disable my-mode."
  (remove-hook 'post-command-hook #'my-post-command t))
```

### Working with Buffers

```elisp
(defun my-package-process-buffer ()
  "Process current buffer."
  (interactive)
  (save-excursion
    (goto-char (point-min))
    (while (not (eobp))
      (process-line)
      (forward-line 1))))
```

### Error Handling

```elisp
(defun my-package-safe-operation ()
  "Perform operation with error handling."
  (condition-case err
      (risky-operation)
    (file-error
     (message "File error: %s" (error-message-string err)))
    (error
     (message "Unexpected error: %s" (error-message-string err)))))
```

### Conditional Loading

```elisp
(with-eval-after-load 'company
  (add-to-list 'company-backends #'my-package-company-backend))
```

## Integration with Claude Code

When Claude Code uses this skill, it will:

1. **Enable lexical binding** in all new files
2. **Add proper package prefixes** to all symbols
3. **Use correct naming conventions** (kebab-case, predicates, etc.)
4. **Write comprehensive docstrings** for all functions
5. **Add autoload cookies** to interactive commands
6. **Follow proper indentation** and formatting
7. **Use preferred syntax** (`when`, `unless`, etc.)
8. **Include proper file headers** and footers
9. **Structure code** according to community conventions
10. **Add appropriate error handling**

## Style Guide Checklist

When writing Emacs Lisp code:

- ✅ File header with `lexical-binding: t`
- ✅ Proper copyright and author information
- ✅ Package metadata (Version, Keywords, URL)
- ✅ Commentary section with description
- ✅ All public symbols prefixed with package name
- ✅ Private functions use double-hyphen prefix
- ✅ Predicates end in `p` or `-p`
- ✅ All functions have docstrings
- ✅ Interactive commands have autoload cookies
- ✅ Proper indentation (spaces only)
- ✅ All closing parens on same line
- ✅ Use `defcustom` for user options
- ✅ Use function quotes (`#'`) for function references
- ✅ File ends with `(provide 'package-name)`
- ✅ File ends with `;;; package-name.el ends here`

## Common Mistakes to Avoid

1. **Forgetting lexical binding declaration**
   ```elisp
   ;;; Bad: no lexical-binding
   ;;; my-package.el --- Description

   ;;; Good:
   ;;; my-package.el --- Description  -*- lexical-binding: t; -*-
   ```

2. **Not prefixing symbols**
   ```elisp
   ;; Bad
   (defun process-data () ...)

   ;; Good
   (defun my-package-process-data () ...)
   ```

3. **Using `if` instead of `when`**
   ```elisp
   ;; Bad
   (if condition
       (progn
         (do-something)
         (do-more)))

   ;; Good
   (when condition
     (do-something)
     (do-more))
   ```

4. **Hard-quoting lambdas**
   ```elisp
   ;; Bad
   (mapcar '(lambda (x) (* x 2)) list)

   ;; Good
   (mapcar (lambda (x) (* x 2)) list)
   ```

5. **Not using autoload cookies**
   ```elisp
   ;; Bad - users must load entire package
   (defun my-package-command () ...)

   ;; Good - command loads package on first use
   ;;;###autoload
   (defun my-package-command () ...)
   ```

## Resources

### Official Documentation
- [GNU Emacs Lisp Reference Manual](https://www.gnu.org/software/emacs/manual/html_node/elisp/)
- [Emacs Lisp Intro](https://www.gnu.org/software/emacs/manual/html_node/eintr/)
- [Emacs Lisp Packaging](https://www.gnu.org/software/emacs/manual/html_node/elisp/Packaging.html)

### Community Resources
- [Emacs Lisp Style Guide](https://github.com/bbatsov/emacs-lisp-style-guide) by Bozhidar Batsov
- [elisp-guide](https://github.com/chrisdone/elisp-guide) by Chris Done
- [EmacsWiki: Emacs Lisp Coding Conventions](https://www.emacswiki.org/emacs/EmacsLispCodingConventions)

### Tools
- **Flycheck with elisp checkers** - Real-time linting
- **Package-lint** - Check package metadata and conventions
- **Checkdoc** - Validate docstrings
- **Elint** - Lint Emacs Lisp code
- **Elisp-lint** - Comprehensive linting tool

## Examples

See the `examples/` directory for complete, working examples:

- **package-template.el** - Complete package structure
- **major-mode.el** - Major mode implementation
- **minor-mode.el** - Minor mode implementation
- **library-functions.el** - Various function patterns

## Contributing

To improve this skill:

1. Test with various Emacs Lisp projects
2. Add more practical examples
3. Document edge cases and gotchas
4. Keep aligned with community conventions
5. Submit improvements to the style guide

## License

This skill is part of the knowhow repository and follows the same license.

## Version History

- **1.0.0** (Initial Release)
  - Complete style guide coverage
  - Layout and formatting rules
  - Naming conventions
  - Documentation standards
  - Common patterns and idioms
  - Quick reference guide

## Acknowledgments

Based on:
- [Emacs Lisp Style Guide](https://github.com/bbatsov/emacs-lisp-style-guide) by Bozhidar Batsov
- Community conventions from popular Emacs packages
- Official Emacs Lisp documentation
- Years of Emacs community best practices
