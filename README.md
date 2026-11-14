# TeXPresso — Scheme programs compiled to plain TeX, implemented in MuLL

TeXPresso is a **working prototype/compiler slice**, not a complete Scheme compiler.
Its lexer, reader, module collector, name resolver, typed integer code generator,
and linker are implemented in **MuLL**, using `MuDSL.hpp`'s MuLL interpreter and
MuLL's existing stdlib. It emits **executable TeX82/plain-TeX programs**, not
LaTeX documents or typesetting code. The TeX runtime uses no font, box, page,
math-typesetting, or shipout primitives.

## What works in this release

- Scheme S-expression reader: parentheses, symbols, signed decimal integers,
  boolean literals, strings, quote syntax (read-only), and `;` comments.
- Separate source modules `(module (name parts) ...)` with `(import ...)`,
  `(export ...)`, dependency validation, stable initialization ordering,
  namespace isolation, and duplicate/ambiguous symbol detection.
- Top-level `(define x expr)` mutable globals and
  `(define (f x ...) expression ...)` fixed-arity procedures.
- Recursive first-order procedures, dynamic activation records, global/local
  mutation, `begin`, `if`, `cond`, `when`, `unless`, `and`, `or`, `let`, `let*`,
  `(while condition body...)` (TeXPresso extension), `set!`.
- 32-bit-range integer literals, checked integer operands, Boolean/integer
  runtime tags (integer zero is **true**, only `#f` is false), `+`, `-`, `*`,
  integer `/` (truncation), `remainder`, `modulo`, `<`, `>`, `<=`, `>=`, `=`,
  `not`, `zero?`.
- `println`, `display`, and `newline`. String literals are supported directly
  as arguments to `println`/`display`, with TeX metacharacters escaped.
- A self-contained generated `.tex` file: the thin Python launcher only loads
  source files, passes their bytes to MuLL, and prepends a static TeX runtime.
- TeX82-compatible dynamic stack frame indexing and first-order calls.

## Not implemented (important)

The TeX82 bootstrap accepts ASCII-only source files (the launcher rejects
non-ASCII bytes). Scheme strings for terminal output are likewise ASCII-only.

This prototype is **not R7RS compliant**. There is no first-class `lambda`,
escaping closure, variable-arity application, `apply`, `letrec`, quoted data
objects, pair/list/vector runtime, arbitrary precision, floating point,
continuations, `syntax-rules`, hygienic macro expander, GC, heap-based Scheme
objects, exceptions, or independent `.tpo`/`.tpi` object linking. Tail calls
still use TeX macro nesting: **proper tail recursion is not guaranteed**.
The `(while ...)` extension is likewise recursion-depth bounded. Only the
TeX82 backend is implemented; e-TeX/pdfTeX specialized backends are future work.

A separate Python launcher is necessary because the existing MuLL standard
library lacks a portable direct filesystem writer/reader. **It contains no
compiler implementation.** It transports complete source strings through MuLL
`Args`, so this bootstrap approach has a conservative 90 KB per-source argument
limit. The compiler is solely in `mull/texpresso_*/Package.mull`.

The numeric backend presently treats all integer arithmetic as engine-sized
TeX count arithmetic; overflow produces an engine error. `/` means truncating
integer division, **not** Scheme's exact rational division. The language's
current `+`, `-`, `*`, and numeric predicates have only 0–2 arguments as
specified in the code generator. `=` and comparisons require exactly two.
String values are not first-class. Except for `println`/`display` string
literals, string and list expressions are explicitly rejected rather than
silently miscompiled.

## Dependency

Use the MuLIB repository at:

https://github.com/Chubek/mulib

MuLL source and definitions:

- `mudsl/MuDSL.hpp`
- `mudsl/mull/` (including `mullier`, `cli`, `native`, `stdlib`)

Build MuLL from the repository root:

```sh
cmake -S mudsl/mull -B build/mull -DMULL_ENABLE_MULIB=OFF
cmake --build build/mull --parallel 4
cmake --install build/mull --prefix "$HOME/.local"
export PATH="$HOME/.local/bin:$PATH"
```

The `texpresso` launcher invokes the installed `mull` program, and package
loading reuses MuLL's `-I` and installed standard library. TeX (the `tex`
command, loading the plain format) is required only to execute generated code.

## Compile and run

From this extracted directory:

```sh
bin/texpresso examples/hello.txp -o hello.tex
tex -interaction=nonstopmode -halt-on-error hello.tex

# Or compile and execute together:
bin/texpresso examples/arith.txp -o arith.tex --run

# Multiple separately named modules (arguments may be in any order):
bin/texpresso examples/modules/app.txp examples/modules/math.txp \
  -o modules.tex --run

# MuLL's D interpreter also works when installed:
bin/texpresso examples/hello.txp --engine=d --run

# Inspect the MuLL syntax without compiling Scheme input:
bin/texpresso examples/hello.txp --check-mull

# Test both MuLL hosts (requires a MuLL installation with the D worker):
make test MULL=/path/to/installed/bin/mull
make check MULL=/path/to/installed/bin/mull ENGINE=d
make example MULL=/path/to/installed/bin/mull ENGINE=d
```

Expected output fragments:

- `hello`: `Hello from TeXPresso!`, then `144`
- `factorial`: `720`
- `arith`: `49`, `2`, `65`, `111`
- `modules`: `27`, `16`

The TeX engine banner and transcript noise may appear alongside these lines.
The resulting TeX program deliberately ends with `\end` without producing
pages.

## Anatomy

- `mull/texpresso_lexer/Package.mull`: complete source scanner.
- `mull/texpresso_reader/Package.mull`: recursive S-expression reader.
- `mull/texpresso_analyzer/Package.mull`: module/linker resolution.
- `mull/texpresso_codegen/Package.mull`: lowering and TeX82 emitter.
- `mull/driver.mull`: MuLL-only compiler driver.
- `runtime/tex82.tex`: executed TeX runtime, prepended to output.
- `bin/texpresso`: filesystem/process bridge (Python 3.9+).
- `tests/`: TeX ABI tests, static shape checks, optional end-to-end MuLL tests.
- `docs/`: architecture, semantics, and next-phase design.

## Test status

The compiler and runtime have been validated with a locally built and installed
MuLL using **both `--engine=cpp` and `--engine=d`**, executing generated programs
under plain `tex -halt-on-error`. Integration tests compare the hosts' generated
TeX byte-for-byte and cover recursion, call-site argument isolation, mixed
integer/boolean arguments, lexical shadowing, string escaping/spacing, module
privacy, diagnostics, and preservation of existing output on compilation errors.
`--check-mull` checks the driver and all four compiler packages.

Run `make test` after installing MuLL. Compiler tests are skipped explicitly
when MuLL is absent; execution tests also require `tex`. Both MuLL hosts are
tested by default. For a C++-only installation, use `make test MULL_ENGINES=cpp`
(or set `MULL_ENGINES=cpp` when invoking unittest directly); this is a reduced
gate, not verification of both hosts. This remains a first-order prototype,
not a Scheme conformance claim.
