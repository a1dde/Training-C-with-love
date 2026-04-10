using System.Text.Json;
using Basic.Reference.Assemblies;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;

if (args.Length < 1)
{
    Console.Error.WriteLine("usage: MeowSyntaxCheck <path-to-Program.cs>");
    Environment.Exit(2);
}

var userPath = Path.GetFullPath(args[0]);
var text = await File.ReadAllTextAsync(userPath);

// Как в учебном проекте: глобальные using из SDK — отдельное дерево, чтобы строки в Program.cs совпадали с редактором
var globalTree = CSharpSyntaxTree.ParseText(
    """
    global using System;
    global using System.Collections.Generic;
    global using System.IO;
    global using System.Linq;
    global using System.Text;
    global using System.Threading.Tasks;
    """,
    path: "GlobalUsings.g.cs");

var userTree = CSharpSyntaxTree.ParseText(
    text,
    CSharpParseOptions.Default.WithLanguageVersion(LanguageVersion.CSharp12),
    userPath);

var refs = Net80.References.All;
var options = new CSharpCompilationOptions(OutputKind.ConsoleApplication)
    .WithNullableContextOptions(NullableContextOptions.Disable);

var compilation = CSharpCompilation.Create(
    "MeowSyntax",
    [globalTree, userTree],
    refs,
    options);

var errList = new List<ErrorJson>();
foreach (var d in compilation.GetDiagnostics())
{
    if (d.Severity != DiagnosticSeverity.Error)
        continue;
    if (d.Location.SourceTree != userTree)
        continue;
    if (!d.Location.IsInSource)
        continue;

    var pos = d.Location.GetLineSpan().StartLinePosition;
    errList.Add(new ErrorJson(
        pos.Line + 1,
        pos.Character + 1,
        d.Id,
        d.GetMessage() ?? ""));
}

var payload = new ResultJson(errList.Count == 0, errList);
Console.WriteLine(JsonSerializer.Serialize(payload, new JsonSerializerOptions
{
    PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
}));

internal sealed record ErrorJson(int Line, int Column, string Code, string Message);

internal sealed record ResultJson(bool Ok, List<ErrorJson> Errors);
