Texture2D<uint> world : register(s0);
Texture1D<float4> colours : register(t1);
RWTexture2D<float4> target : register(u0);

[numthreads(8,8,1)]
void main(int3 global_pos : SV_DispatchThreadID)
{
    int2 pos = global_pos.xy;
    //float4 data = colours[0][0];
    target[pos] = colours[world[pos/10]];
    //target[pos] = float4(1,1,0,1);
}