# Journal Entry: Building a Read-Only MCP for Cascade CMS

## 1. The Problem

I was asked to write a script that could edit data structure nodes in Cascade CMS. Those nodes come from the JSON REST responses derived from Cascade's data definitions. My first helper function could traverse the nodes and find a match by group node and identifier, but I still had to check the data definition mapping side by side. That worked for me as a human. It did not work for a code agent.

The later script needed to update many element types: radio buttons, text fields, WYSIWYG, dropdowns, multi-select, and more. That went far beyond the widget editing in my earlier XML edit script. My workflow became painful. I ran raw reads through Postman, copied the output into JSON files, and wrote XML files for the raw data definitions. Then I gave those files to the agent as context. The results were decent, but the agent spent more reasoning effort and more tokens than it should have.

## 2. The Idea

The MCP idea came when those scenarios made the cost of the manual loop obvious. Earlier, when I first built the skill file, I thought about an MCP but could not find a real use for it, so I did not build one. When the need became clear, I saw that a read-only MCP would fit. If an agent can read the live structure directly, it can check its own assumptions. A skill file alone cannot do that.

## 3. The Decision: Read-Only

Read-only was intentional. While researching Cascade MCPs, I found one that gave agents full write access. I thought that was too risky. What if the agent hallucinated, or I accidentally pointed it at a production server? My instinct came first. The reasoning came after.

The MCP only needs to verify that a script is structurally sound. Writes stay in the skill package, for `edit` and `create` operations, and I run those tests myself. This also protects against prompt injection and other attacks on AI agents. I also assumed the credentials might be over-scoped, so the design should not depend on them being least-privilege.

## 4. The Gap

Before I changed anything, I ran a few live searches on my own. They showed that the `users` asset type was exposed. I then read a real user asset to confirm which sensitive data came back. The type guard alone was not enough. Fields such as `createdBy` could still carry a person's name and email. Those values are not secrets like passwords or API keys, but they are personal information tied to the organization.

## 5. The Fix

I had Claude Code implement the changes. Then I had it generate adversarial test prompts to probe the MCP directly. I asked specifically for rare edge cases and prompting workarounds. Some gaps appeared, and I had them fixed before pushing.

The current behavior is this. Sensitive asset types are dropped unless they are explicitly searched for. Fields like `createdBy` stay in the response, but their values are replaced with `[REDACTED]`. This keeps the response shape intact, so the agent can still use it as a template.

## 6. Reflection

At first, simplicity mattered most. I wanted the agent to have full context, not small fragments. The response shape was a template the agent could reference, and at that stage prototyping speed mattered more than redaction. Filtering would have slowed me down while I was still learning what the scripts needed.

When the MCP became a real tool, security became a requirement. Authorship information was not essential to the agent's work, so the cost of exposing it outweighed the convenience of keeping it. That shift is where I draw the line.

AI-based testing has blind spots. The model may be unreliable, and so may the tests it generates. I cannot test every possible scenario, so I focus on the most prevalent failure patterns. Testing is risk management under uncertainty, not proof. Security decisions depend on risk tolerance, and that tolerance has to be chosen deliberately.
