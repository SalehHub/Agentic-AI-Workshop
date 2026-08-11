from agents import RunHooks


class ConsoleHooks(RunHooks):
    async def on_agent_start(self, context, agent):
        # print(f"\n[Agent started] {agent.name}")
        pass

    async def on_llm_start(
        self,
        context,
        agent,
        system_prompt,
        input_items,
    ):
        print("[Thinking] The model is processing the request...")

    async def on_llm_end(self, context, agent, response):
        # print("[Thinking finished]")
        pass

    async def on_tool_start(self, context, agent, tool):
        print(f"[Tool started] {tool.name}")

        tool_arguments = getattr(
            context,
            "tool_arguments",
            None,
        )

        if tool_arguments:
            print(f"[Tool arguments] {tool_arguments}")

    async def on_tool_end(
        self,
        context,
        agent,
        tool,
        result,
    ):
        # print(f"[Tool finished] {tool.name}")
        print(f"[Tool result]\n{result}")

    # async def on_handoff(
    #     self,
    #     context,
    #     from_agent,
    #     to_agent,
    # ):
    #     print(f"[Handoff] {from_agent.name} " f"to {to_agent.name}")

    async def on_agent_end(
        self,
        context,
        agent,
        output,
    ):
        print(f"[Agent finished] {agent.name}")
