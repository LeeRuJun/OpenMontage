from types import SimpleNamespace

from tools.base_tool import ToolRuntime, ToolStatus
from tools.tool_registry import ToolRegistry, is_logically_disabled


def _tool(name, capability, runtime, provider, status=ToolStatus.AVAILABLE):
    return SimpleNamespace(
        name=name,
        capability=capability,
        capabilities=[capability],
        runtime=runtime,
        provider=provider,
        tier=SimpleNamespace(value="generate"),
        stability=SimpleNamespace(value="production"),
        resource_profile=SimpleNamespace(vram_mb=0, network_required=True),
        best_for=[provider],
        dependencies=[],
        install_instructions="",
        fallback_tools=[],
        fallback=None,
        get_status=lambda: status,
        get_info=lambda: {
            "name": name,
            "provider": provider,
            "status": status.value,
            "dependencies": [],
        },
    )


def test_local_image_and_video_tools_are_logically_disabled():
    registry = ToolRegistry()
    local_image = _tool(
        "local_diffusion", "image_generation", ToolRuntime.LOCAL_GPU, "local_diffusion"
    )
    local_video = _tool("wan_video", "video_generation", ToolRuntime.LOCAL_GPU, "wan")
    remote_image = _tool("openai_image", "image_generation", ToolRuntime.API, "openai")
    remote_video = _tool("veo_video", "video_generation", ToolRuntime.API, "veo")
    for tool in (local_image, local_video, remote_image, remote_video):
        registry.register(tool)

    assert is_logically_disabled(local_image)
    assert is_logically_disabled(local_video)
    assert [tool.name for tool in registry.get_by_capability("image_generation")] == [
        "openai_image"
    ]
    assert [tool.name for tool in registry.get_by_capability("video_generation")] == [
        "veo_video"
    ]


def test_provider_menu_marks_local_media_disabled_and_does_not_configure_it():
    registry = ToolRegistry()
    local_image = _tool(
        "local_diffusion", "image_generation", ToolRuntime.LOCAL_GPU, "local_diffusion"
    )
    remote_image = _tool("openai_image", "image_generation", ToolRuntime.API, "openai")
    registry.register(local_image)
    registry.register(remote_image)
    registry._discovered_packages.add("tools")

    menu = registry.provider_menu()
    image_menu = menu["image_generation"]
    assert image_menu["configured"] == 1
    assert [item["name"] for item in image_menu["available"]] == ["openai_image"]
    disabled = next(
        item for item in image_menu["unavailable"] if item["name"] == "local_diffusion"
    )
    assert disabled["status"] == "disabled"
    assert "disabled by policy" in disabled["disabled_reason"]


def test_disabled_tools_are_not_available_fallbacks():
    registry = ToolRegistry()
    local_image = _tool(
        "local_diffusion", "image_generation", ToolRuntime.LOCAL_GPU, "local_diffusion"
    )
    remote_image = _tool("openai_image", "image_generation", ToolRuntime.API, "openai")
    caller = _tool("image_selector", "image_generation", ToolRuntime.HYBRID, "selector")
    caller.fallback_tools = ["local_diffusion", "openai_image"]
    for tool in (local_image, remote_image, caller):
        registry.register(tool)

    assert registry.find_fallback("image_selector").name == "openai_image"
