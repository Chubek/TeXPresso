# TeXPresso agent instructions

## Project identity

TeXPresso is a Scheme dialect that compiles executable programs into TeX82,
not a typesetting engine. It must not emit LaTeX, page boxes, fonts, or shipout.
The compiler implementation language is **MuLL**, from the MuLIB repository
under `mudsl/mull`. `MuDSL.hpp` and `MuDSL.d` are the embedding hosts. Do not
replace the compiler with Python/C++ code; the Python launcher is only for I/O.

## Existing behavior

Maintain the MuLL four-package compiler architecture and the TeX82 runtime ABI:
`TP@result`, `TP@tag`, `TP@frame`, `TP@load`, `TP@loadtag`, `TP@store`,
`TP@enter`, `TP@leave`, `TP@caller`, `TP@callertag`, `TP@copycaller`,
`TP@gload`, `TP@gstore`, `TP@truthvalue`, `TP@settruth`.

Correctness requirements:
- Scheme truth: only #f is false, integers including 0 are true.
- Each recursive invocation must receive independent local variable slots.
- Argument slots belong to a **call site**, not one fixed per-frame area.
- Module imports must resolve only exported definitions, not private names.
- TeX output must run without LaTeX or document output.
- Failed compilation should never create or overwrite an output program.
- Unsupported language forms must produce an explicit diagnostic.

## Next milestones

1. Build and test the MuLL compiler with both `--engine=cpp` and `--engine=d`.
   Fix interpreter-specific syntax/semantic mismatches before expanding scope.
2. Replace argument-based transport with a dedicated MuLL host I/O package,
   retaining all compilation passes in MuLL.
3. Implement tagged heap values, shared mutable captured cells, lexical
   closure conversion, and first-class procedure calls.
4. Introduce ANF and CPS or explicit TPAM bytecode lowering, with a genuinely
   bounded dispatcher and proper tail recursion.
5. Implement pairs, lists, vectors, strings, bytevectors and a collector.
6. Implement exact Scheme integers/rationals instead of TeX count-only math.
7. Add hygienic macro expansion and conformance suites.
8. Add independent `.tpo` object files, `.tpi` interfaces and relocatable link.
9. Specialize pure expressions to TeX expansion; add e-TeX/pdfTeX profiles.
10. Stress-test limits: TeX hash size, input/parameter/expansion stack,
    string pool, register count, numeric overflow, and file I/O.

## Testing and gates

Run `python3 -m unittest discover -s tests -v`, `make check`, and
`make example`, all with a locally installed MuLL. Use `tex -halt-on-error`.
No test should claim complete Scheme conformance until the missing runtime
features have been independently implemented and validated.
